app_name = "pk_integrations"
app_title = "PK Integrations"
app_publisher = "Nesway"
app_description = "Pakistan integrations for Frappe: PostEx courier and local payment gateways"
app_email = "imran.ali@nesway.com"
app_license = "gpl-3.0"

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "pk_integrations",
# 		"logo": "/assets/pk_integrations/logo.png",
# 		"title": "PK Integrations",
# 		"route": "/pk_integrations",
# 		"has_permission": "pk_integrations.api.permission.has_app_permission",
# 	}
# ]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `pk_integrations/dock/pk_integrations/pk_integrations.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pk_integrations/css/pk_integrations.css"
# app_include_js = "/assets/pk_integrations/js/pk_integrations.js"

# include js, css files in header of web template
# web_include_css = "/assets/pk_integrations/css/pk_integrations.css"
# web_include_js = "/assets/pk_integrations/js/pk_integrations.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pk_integrations/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "pk_integrations/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "pk_integrations.utils.jinja_methods",
# 	"filters": "pk_integrations.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "pk_integrations.install.before_install"
# after_install = "pk_integrations.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "pk_integrations.uninstall.before_uninstall"
# after_uninstall = "pk_integrations.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "pk_integrations.utils.before_app_install"
# after_app_install = "pk_integrations.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "pk_integrations.utils.before_app_uninstall"
# after_app_uninstall = "pk_integrations.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "pk_integrations.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "pk_integrations.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pk_integrations.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["pk_integrations.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# P1.11: failed outside calls are tried again (3 tries, waiting 5, 10, 20 minutes)
scheduler_events = {
	"cron": {
		"*/5 * * * *": ["pk_integrations.base.retry_due"],
	},
}

# scheduler_events = {
# 	"all": [
# 		"pk_integrations.tasks.all"
# 	],
# 	"daily": [
# 		"pk_integrations.tasks.daily"
# 	],
# 	"hourly": [
# 		"pk_integrations.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pk_integrations.tasks.weekly"
# 	],
# 	"monthly": [
# 		"pk_integrations.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "pk_integrations.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "pk_integrations.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pk_integrations.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pk_integrations.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["pk_integrations.utils.before_request"]
# after_request = ["pk_integrations.utils.after_request"]

# Job Events
# ----------
# before_job = ["pk_integrations.utils.before_job"]
# after_job = ["pk_integrations.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"pk_integrations.auth.validate"
# ]

# on_social_login = "pk_integrations.auth.on_social_login"

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []
