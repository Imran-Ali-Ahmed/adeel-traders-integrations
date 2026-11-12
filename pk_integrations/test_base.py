"""P1.11: the integration framework logs every try, never sends a done call twice, retries
failed calls with a growing wait, and alerts the owner after the last try."""

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_to_date, now_datetime

from pk_integrations import base

CALLS = []


def fake_ok(payload):
	CALLS.append(payload)
	return {"tracking": "PX-" + payload["order"]}


def fake_fail(payload):
	CALLS.append(payload)
	raise ConnectionError("PostEx is not answering")


def _age(key, minutes):
	"""Pretend the last try was made some minutes ago."""
	for name in frappe.get_all("Integration Request", filters={"request_id": key}, pluck="name"):
		frappe.db.set_value(
			"Integration Request",
			name,
			"modified",
			add_to_date(now_datetime(), minutes=-minutes),
			update_modified=False,
		)


class TestIntegrationBase(IntegrationTestCase):
	def setUp(self):
		CALLS.clear()
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.db.delete("Integration Request", {"request_id": ["like", "_test-%"]})
		frappe.db.delete("Notification Log", {"subject": ["like", "%_test%"]})

	def test_success_is_logged_and_never_sent_twice(self):
		key = "_test-ok-1"
		out = base.run("postex", "Book order", "pk_integrations.test_base.fake_ok", {"order": "1"}, key)
		self.assertEqual(out, {"tracking": "PX-1"})
		again = base.run("postex", "Book order", "pk_integrations.test_base.fake_ok", {"order": "1"}, key)
		self.assertEqual(again, out)
		self.assertEqual(len(CALLS), 1)  # the courier saw one booking
		self.assertEqual(
			frappe.db.count("Integration Request", {"request_id": key, "status": "Completed"}), 1
		)

	def test_failure_is_retried_with_growing_wait_then_alerts(self):
		key = "_test-fail-1"
		self.assertIsNone(
			base.run("postex", "Book order _test", "pk_integrations.test_base.fake_fail", {"order": "2"}, key)
		)
		base.retry_due()
		self.assertEqual(len(CALLS), 1)  # too early: waits 5 minutes
		_age(key, 6)
		base.retry_due()
		self.assertEqual(len(CALLS), 2)
		_age(key, 9)
		base.retry_due()
		self.assertEqual(len(CALLS), 2)  # second wait is 10 minutes
		with patch.object(base, "_alert") as alert:
			_age(key, 11)
			base.retry_due()
			self.assertEqual(len(CALLS), 3)
			alert.assert_called_once()  # last try failed: the owner is told
		_age(key, 60)
		base.retry_due()
		self.assertEqual(len(CALLS), 3)  # no fourth automatic try

	def test_retry_after_fix_succeeds_and_status_shows_it(self):
		key = "_test-fix-1"
		base.run("postex", "Book order", "pk_integrations.test_base.fake_fail", {"order": "3"}, key)
		failed = frappe.get_all("Integration Request", filters={"request_id": key}, pluck="name")[0]
		state = base.status()
		self.assertFalse(next(s for s in state["services"] if s["key"] == "postex")["connected"])
		row = next(c for c in state["calls"] if c["name"] == failed)
		self.assertTrue(row["can_retry"])
		self.assertIn("not answering", row["error"])
		frappe.db.set_value(
			"Integration Request",
			failed,
			"data",
			frappe.as_json(
				{"payload": {"order": "3"}, "method": "pk_integrations.test_base.fake_ok", "attempt": 1}
			),
		)
		self.assertTrue(base.retry(failed)["ok"])
		self.assertFalse(next(c for c in base.status()["calls"] if c["name"] == failed)["can_retry"])

	def test_status_needs_permission(self):
		user = "_test_pk_counter@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{"doctype": "User", "email": user, "first_name": "T", "send_welcome_email": 0}
			).insert().add_roles("Sales User")
		frappe.set_user(user)
		with self.assertRaises(frappe.PermissionError):
			base.status()
