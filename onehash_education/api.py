import frappe
from pypika import Order
from frappe import utils as frappe_utils
from onehash_education import utils


@frappe.whitelist(allow_guest=True)
def get_admission_years():
    return frappe.db.get_all("Academic Year", ["name"], {"admission_open": 1})


@frappe.whitelist(allow_guest=True)
def get_admission_year_groups(academic_year):
    return frappe.db.get_all(
        "Year Groups",
        ["year_group"],
        {
            "parenttype": "Academic Year",
            "parentfield": "admissions_open_for",
            "parent": academic_year,
        },
    )


@frappe.whitelist(allow_guest=True)
def get_admission_years_and_groups():
    admission_data = {}

    admission_years = get_admission_years()

    for admission_year in admission_years:
        admission_year_group = get_admission_year_groups(admission_year["name"])

        admission_data[admission_year["name"]] = [
            yg["year_group"] for yg in admission_year_group
        ]

    return admission_data


@frappe.whitelist()
def enroll_student(applicant_name, terms):
    frappe.publish_realtime(
        "enroll_student_progress", {"progress": [1, 4]}, user=frappe.session.user
    )

    if isinstance(terms, str):
        terms = frappe.parse_json(terms)
    if not terms:
        frappe.throw("Terms are required")

    student_applicant = frappe.db.get_value(
        "Student Applicant",
        applicant_name,
        [
            "year_group",
            "academic_year",
            "first_name",
            "middle_name",
            "last_name",
            "applicant_name",
            "student_image",
        ],
        as_dict=True,
    )
    if not student_applicant:
        frappe.throw("Student Applicant not found.")

    student = frappe.new_doc("Student")
    student.enabled = True
    student.first_name = student_applicant.first_name
    student.middle_name = student_applicant.middle_name
    student.last_name = student_applicant.last_name
    student.student_name = student_applicant.applicant_name
    student.user_id = student_applicant.student_user
    student.student_applicant = applicant_name
    student.student_image = student_applicant.student_image
    student.customer = student_applicant.customer
    student.save()

    program_enrollments = []
    for term in terms:
        program_enrollment = frappe.new_doc("Program Enrollment")
        program_enrollment.student = student.name
        program_enrollment.student_name = student.student_name
        program_enrollment.year_group = student_applicant.year_group
        program_enrollment.academic_year = student_applicant.academic_year
        program_enrollment.academic_term = term
        program_enrollment.enrollment_date = frappe_utils.nowdate()
        program_enrollment.created_by_enrollment_tool = True
        program_enrollment.save()
        program_enrollments.append(program_enrollment.name)

    frappe.db.set_value("Student Applicant", applicant_name, "enrolled", 1)
    frappe.publish_realtime(
        "enroll_student_progress", {"progress": [2, 4]}, user=frappe.session.user
    )

    frappe.response["message"] = program_enrollments


@frappe.whitelist()
def get_user_info():
    if frappe.session.user == "Guest":
        frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

    current_user = frappe.db.get_list(
        "User",
        fields=["name", "email", "enabled", "user_image", "full_name", "user_type"],
        filters={"name": frappe.session.user},
    )[0]
    current_user["session_user"] = True
    return current_user


@frappe.whitelist()
def get_students():
    user = frappe.session.user
    user_roles = frappe.get_roles()
    students = []

    if "Student" in user_roles:
        students = frappe.db.get_list(
            "Student",
            fields=[
                "customer",
                "name",
                "student_applicant",
                "student_image",
                "student_name",
            ],
            filters={"user_id": user, "enabled": 1},
            order_by="creation asc",
        )

    applicants = frappe.db.get_list(
        "Student Applicant",
        fields=[
            "customer",
            "name as student_applicant",
            "student_image",
            "applicant_name as student_name",
        ],
        filters={"student_user": user, "enrolled": 0},
        order_by="creation asc",
    )
    for applicant in applicants:
        applicant["is_applicant"] = True
    students.extend(applicants)

    return students


@frappe.whitelist()
def get_customer_transactions(customer, page_length=20, page=0):
    if not customer:
        frappe.throw("Customer is required.")

    frappe.has_permission("Customer", "read", customer, throw=True)

    Customer = frappe.qb.DocType("Customer")
    SalesInvoice = frappe.qb.DocType("Sales Invoice")
    PaymentEntryReference = frappe.qb.DocType("Payment Entry Reference")
    PaymentEntry = frappe.qb.DocType("Payment Entry")

    transactions = (
        frappe.qb.from_(SalesInvoice)
        .join(Customer)
        .on((Customer.name == customer) & (Customer.name == SalesInvoice.customer))
        .left_join(PaymentEntryReference)
        .on(
            (PaymentEntryReference.reference_doctype == "Sales Invoice")
            & (PaymentEntryReference.parenttype == "Payment Entry")
            & (SalesInvoice.name == PaymentEntryReference.reference_name)
        )
        .left_join(PaymentEntry)
        .on(
            (PaymentEntry.docstatus == 1)
            & (PaymentEntry.name == PaymentEntryReference.parent)
        )
        .select(
            SalesInvoice.name.as_("invoice"),
            SalesInvoice.currency,
            SalesInvoice.due_date,
            SalesInvoice.status,
            SalesInvoice.outstanding_amount,
            SalesInvoice.grand_total.as_("amount"),
            SalesInvoice.custom_academic_year.as_("academic_year"),
            SalesInvoice.custom_year_group.as_("year_group"),
            PaymentEntry.name.as_("receipt"),
            PaymentEntry.posting_date.as_("payment_date"),
        )
        .where(
            (SalesInvoice.docstatus == 1)
            & ((SalesInvoice.status != "Paid") | (PaymentEntry.name.isnotnull()))
        )
        .orderby(SalesInvoice.creation, order=Order.desc)
        .limit(page_length)
        .offset(page)
        .run(as_dict=True)
    )

    for transaction in transactions:
        if transaction.amount and transaction.currency:
            transaction["formatted_amount"] = frappe_utils.fmt_money(
                transaction.amount, currency=transaction.currency
            )
        else:
            transaction["formatted_amount"] = transaction.amount

    return {
        "transactions": transactions,
        "invoice_format": utils.get_default_print_format("Sales Invoice"),
        "receipt_format": utils.get_default_print_format("Payment Entry"),
    }


@frappe.whitelist()
def get_invoices_to_pay(customer):
    if not customer:
        frappe.throw("Customer is required.")

    frappe.has_permission("Customer", "read", customer, throw=True)

    invoice_open_statuses = [
        "Submitted",
        "Partly Paid",
        "Unpaid",
        "Unpaid and Discounted",
        "Partly Paid and Discounted",
        "Overdue and Discounted",
        "Overdue",
    ]

    SalesInvoice = frappe.qb.DocType("Sales Invoice")
    SalesInvoiceItem = frappe.qb.DocType("Sales Invoice Item")

    invoices = (
        frappe.qb.from_(SalesInvoice)
        .join(SalesInvoiceItem)
        .on(
            (SalesInvoiceItem.parenttype == "Sales Invoice")
            & (SalesInvoiceItem.parent == SalesInvoice.name)
        )
        .select(
            SalesInvoice.name,
            SalesInvoice.due_date,
            SalesInvoice.currency,
            SalesInvoice.grand_total,
            SalesInvoice.outstanding_amount.as_("payable_amount"),
            SalesInvoiceItem.amount.as_("item_amount"),
            SalesInvoiceItem.item_name,
        )
        .where(
            (SalesInvoice.status.isin(invoice_open_statuses))
            & (SalesInvoice.customer == customer)
        )
        .run(as_dict=True)
    )

    grouped_invoices = []

    last_invoice = None
    for invoice in invoices:

        if last_invoice and invoice["name"] != invoice.name:
            grouped_invoices.append(last_invoice)
            last_invoice = None

        if not last_invoice:
            last_invoice = {
                "name": invoice.name,
                "due_date": invoice.due_date,
                "currency": invoice.currency,
                "grand_total": invoice.grand_total,
                "grand_total_formatted": frappe_utils.fmt_money(
                    invoice.grand_total, currency=invoice.currency
                ),
                "payable_amount": invoice.payable_amount,
                "payable_amount_formatted": frappe_utils.fmt_money(
                    invoice.payable_amount, currency=invoice.currency
                ),
                "items": [],
            }

        item = {
            "item_name": invoice.item_name,
            "item_amount": invoice.item_amount,
            "item_amount_formatted": frappe_utils.fmt_money(
                invoice.item_amount, currency=invoice.currency
            ),
        }
        if item not in last_invoice["items"]:
            last_invoice["items"].append(item)

    if last_invoice and last_invoice not in grouped_invoices:
        grouped_invoices.append(last_invoice)
    return grouped_invoices


@frappe.whitelist()
def get_school_abbr_logo():
    abbr = frappe.db.get_single_value(
        "Education Settings", "school_college_name_abbreviation"
    )
    logo = frappe.db.get_single_value("Education Settings", "school_college_logo")
    return {"name": abbr, "logo": logo}
