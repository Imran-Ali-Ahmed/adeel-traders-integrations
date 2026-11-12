"""Integration framework (Adeel Traders roadmap P1.11): one safe way to call outside services
(PostEx in Phase 8, the payment gateway in Phase 10, the attendance machine in Phase 11).

Built on Frappe's Integration Request (one log row per try: service, action, request, answer,
error, linked document). This module adds:
  - no double sending: a call with the same key that already succeeded returns the saved answer,
  - retry: a failed call is tried again by the scheduler, 3 tries, waiting 5, 10, 20 minutes,
  - alert: when the last try fails, owners get a bell notification (and an email once sending is on),
  - status for the staff app's Settings > Integrations page.

How a later phase uses it (example, PostEx booking):
	from pk_integrations.base import run
	run("postex", "Book order", "pk_integrations.postex.book", {"order": "SO-0001"},
	    key="postex-book-SO-0001", reference=("Sales Order", "SO-0001"))
The method gets the payload and returns a JSON-able answer, or raises on failure.
"""

import json
import traceback
from dataclasses import dataclass

import frappe
from frappe import _
from frappe.utils import add_to_date, cint, cstr, now_datetime

MAX_TRIES = 3
FIRST_WAIT_MINUTES = 5  # then 10, then 20


@dataclass(frozen=True)
class Service:
	label: str
	purpose: str
	phase: str


# Each service is switched on by its phase (settings + credentials). Until then: "Not connected".
SERVICES: dict[str, Service] = {
	"postex": Service(
		"PostEx", "Book courier orders, print airway bills, track delivery and cash", "Phase 8"
	),
	"payment_gateway": Service("Payment gateway", "Card and wallet payments on the website", "Phase 10"),
	"attendance": Service("Attendance machine", "Daily check-in and check-out of staff", "Phase 11"),
}


def _connected(service: str) -> bool:
	"""A phase that adds a service sets this flag when its settings are complete."""
	return bool(cint(frappe.conf.get(f"pk_{service}_enabled")))


def _service(service: str) -> Service:
	if service not in SERVICES:
		frappe.throw(_("Unknown service {0}").format(service))
	return SERVICES[service]


def _done(service: str, key: str):
	return frappe.db.get_value(
		"Integration Request",
		{"integration_request_service": _service(service).label, "request_id": key, "status": "Completed"},
		"output",
	)


def _tries(service: str, key: str) -> int:
	return frappe.db.count(
		"Integration Request", {"integration_request_service": _service(service).label, "request_id": key}
	)


def run(
	service: str,
	action: str,
	method: str,
	payload: dict,
	key: str,
	reference: tuple[str, str] | None = None,
):
	"""Call `method(payload)` once and log it. Returns the answer, or None when it failed
	(the scheduler tries again). A key that already succeeded is never sent again."""
	label = _service(service).label
	if (saved := _done(service, key)) is not None:
		return json.loads(saved) if saved else None
	attempt = _tries(service, key) + 1
	log = frappe.get_doc(
		{
			"doctype": "Integration Request",
			"integration_request_service": label,
			"request_description": action,
			"request_id": key,
			"status": "Queued",
			"is_remote_request": 0,
			"data": json.dumps({"payload": payload, "method": method, "attempt": attempt}, default=str),
			"reference_doctype": reference[0] if reference else None,
			"reference_docname": reference[1] if reference else None,
		}
	).insert(ignore_permissions=True)
	try:
		answer = frappe.get_attr(method)(payload)
	except Exception:
		log.db_set({"status": "Failed", "error": traceback.format_exc()[-4000:]})
		if attempt >= MAX_TRIES:
			_alert(label, action, key, log.name)
		return None
	log.db_set({"status": "Completed", "output": json.dumps(answer, default=str)})
	return answer


def _alert(label: str, action: str, key: str, log_name: str) -> None:
	from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification

	owners = {
		u
		for u in frappe.get_all(
			"Has Role", filters={"role": "System Manager", "parenttype": "User"}, pluck="parent"
		)
		if u not in ("Administrator", "Guest") and frappe.db.get_value("User", u, "enabled")
	}
	if owners:
		enqueue_create_notification(
			list(owners),
			{
				"type": "Alert",
				"subject": _("{0} failed {1} times: {2}").format(label, MAX_TRIES, action),
				"document_type": "Integration Request",
				"document_name": log_name,
				"link": "/settings/integrations",
			},
		)


def retry_due() -> None:
	"""Scheduler (every 5 minutes): try failed calls again, waiting longer after each try."""
	latest: dict[tuple, dict] = {}
	for r in frappe.get_all(
		"Integration Request",
		filters={
			"integration_request_service": ["in", [s.label for s in SERVICES.values()]],
			"request_id": ["is", "set"],
		},
		fields=["name", "integration_request_service", "request_id", "status", "data", "modified"],
		order_by="creation asc",
	):
		latest[(r.integration_request_service, r.request_id)] = r
	by_label = {s.label: k for k, s in SERVICES.items()}
	for (label, key), r in latest.items():
		if r.status != "Failed":
			continue
		data = json.loads(r.data or "{}")
		attempt = cint(data.get("attempt"))
		wait = FIRST_WAIT_MINUTES * 2 ** (attempt - 1)
		if attempt >= MAX_TRIES or r.modified > add_to_date(now_datetime(), minutes=-wait):
			continue
		ref = frappe.db.get_value("Integration Request", r.name, ["reference_doctype", "reference_docname"])
		run(
			by_label[label],
			_action(r.name),
			data["method"],
			data["payload"],
			key,
			tuple(ref) if ref and ref[0] else None,
		)


def _action(log_name: str) -> str:
	return frappe.db.get_value("Integration Request", log_name, "request_description") or ""


# ---------------------------------------------------------------------------
# Settings > Integrations (staff app)
# ---------------------------------------------------------------------------


def _require():
	if not frappe.has_permission("Integration Request", "read"):
		frappe.throw(_("You do not have permission to see integrations."), frappe.PermissionError)


@frappe.whitelist(methods=["GET"])
def status() -> dict:
	"""Each service: connected or not, last call, failures in the last 7 days; and the latest calls."""
	_require()
	week = add_to_date(now_datetime(), days=-7)
	services = []
	for key, s in SERVICES.items():
		last = frappe.get_all(
			"Integration Request",
			filters={"integration_request_service": s.label},
			fields=["creation", "status"],
			order_by="creation desc",
			limit=1,
		)
		services.append(
			{
				"key": key,
				"label": s.label,
				"purpose": s.purpose,
				"phase": s.phase,
				"connected": _connected(key),
				"last_call": cstr(last[0].creation) if last else None,
				"last_status": last[0].status if last else None,
				"failed_7_days": frappe.db.count(
					"Integration Request",
					{"integration_request_service": s.label, "status": "Failed", "creation": [">=", week]},
				),
			}
		)
	calls = frappe.get_all(
		"Integration Request",
		filters={"integration_request_service": ["in", [s.label for s in SERVICES.values()]]},
		fields=[
			"name",
			"integration_request_service",
			"request_description",
			"status",
			"creation",
			"error",
			"request_id",
			"data",
			"reference_doctype",
			"reference_docname",
		],
		order_by="creation desc",
		limit=30,
	)
	return {
		"services": services,
		"calls": [
			{
				"name": c.name,
				"service": c.integration_request_service,
				"action": c.request_description,
				"status": c.status,
				"at": cstr(c.creation),
				"attempt": cint(json.loads(c.data or "{}").get("attempt")),
				"error": (cstr(c.error).strip().splitlines() or [""])[-1][:200],
				"reference": [c.reference_doctype, c.reference_docname] if c.reference_doctype else None,
				"can_retry": c.status == "Failed"
				and _done_label(c.integration_request_service, c.request_id) is None,
			}
			for c in calls
		],
		"max_tries": MAX_TRIES,
	}


def _done_label(label: str, key: str | None):
	if not key:
		return None
	return frappe.db.get_value(
		"Integration Request",
		{"integration_request_service": label, "request_id": key, "status": "Completed"},
		"name",
	)


@frappe.whitelist(methods=["POST"])
def retry(name: str) -> dict:
	"""Try one failed call again now (owner's "Retry" button)."""
	_require()
	if not frappe.has_permission("Integration Request", "write"):
		frappe.throw(_("You do not have permission to retry calls."), frappe.PermissionError)
	r = frappe.get_doc("Integration Request", name)
	if r.status != "Failed":
		frappe.throw(_("Only a failed call can be tried again."))
	by_label = {s.label: k for k, s in SERVICES.items()}
	if r.integration_request_service not in by_label:
		frappe.throw(_("This call does not belong to a known service."))
	data = json.loads(r.data or "{}")
	ref = (r.reference_doctype, r.reference_docname) if r.reference_doctype else None
	answer = run(
		by_label[r.integration_request_service],
		r.request_description,
		data["method"],
		data["payload"],
		r.request_id,
		ref,
	)
	return {"ok": answer is not None}
