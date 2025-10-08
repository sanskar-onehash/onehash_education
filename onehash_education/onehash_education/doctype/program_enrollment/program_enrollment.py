# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from frappe.model.document import Document


class ProgramEnrollment(Document):
    def validate(self):
        self.set_student_name()
        self.validate_duplication()
        self.validate_academic_term()

    def before_save(self):
        self.set_status()
        self.validate()

    def before_submit(self):
        self.set_status()
        self.validate()

    def set_student_name(self):
        if not self.student_name:
            self.student_name = frappe.db.get_value(
                "Student", self.student, "student_name"
            )

    def set_status(self):
        current_date = utils.getdate()
        academic_term_doc = frappe.get_doc("Academic Term", self.academic_term)

        if academic_term_doc.term_start_date > current_date:
            self.status = "Upcoming"
        elif academic_term_doc.term_end_date < current_date:
            self.status = "Expired"
        else:
            self.status = "Active"

    def validate_duplication(self):
        enrollment = frappe.db.exists(
            "Program Enrollment",
            {
                "student": self.student,
                "year_group": self.year_group,
                "academic_year": self.academic_year,
                "academic_term": self.academic_term,
                "docstatus": ("<", 2),
                "name": ("!=", self.name),
            },
        )
        if enrollment:
            frappe.throw(frappe._("Student is already enrolled."))

    def validate_academic_term(self):
        frappe.get_doc("Academic Term", self.academic_term).validate_term_date_range(
            self.academic_year
        )


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_students(doctype, txt, searchfield, start, page_len, filters):
    education_settings = frappe.get_single("Education Settings")
    if not filters.get("academic_term"):
        filters["academic_term"] = education_settings.current_academic_term

    if not filters.get("academic_year"):
        filters["academic_year"] = education_settings.current_academic_year

    enrolled_students = frappe.get_list(
        "Program Enrollment",
        filters={
            "academic_term": filters.get("academic_term"),
            "academic_year": filters.get("academic_year"),
        },
        fields=["student"],
    )

    students = [d.student for d in enrolled_students] if enrolled_students else [""]

    return frappe.db.sql(
        """select
			name, student_name from tabStudent
		where
			name not in (%s)
		and
			`%s` LIKE %s
		order by
			idx desc, name
		limit %s, %s"""
        % (", ".join(["%s"] * len(students)), searchfield, "%s", "%s", "%s"),
        tuple(students + ["%%%s%%" % txt, start, page_len]),
    )


@frappe.whitelist()
def get_active_enrollment(student):
    if not student:
        frappe.throw("Student ID is required")

    current_date = utils.getdate()

    result = frappe.db.sql(
        """
        SELECT pe.name, pe.student_name, pe.year_group, pe.academic_year, pe.academic_term
        FROM `tabProgram Enrollment` pe
        JOIN `tabAcademic Term` at ON pe.academic_term = at.name
        WHERE pe.student = %s
        AND %s BETWEEN at.term_start_date AND at.term_end_date
        ORDER BY at.term_start_date ASC
        LIMIT 1
    """,
        (student, current_date),
        as_dict=True,
    )

    return result[0] if result else None


@frappe.whitelist()
def get_nearest_enrollment(student):
    upcoming_enrollments = get_upcoming_enrollments(student)

    return upcoming_enrollments[0] if upcoming_enrollments else None


@frappe.whitelist()
def get_upcoming_enrollments(student):
    if not student:
        frappe.throw("Student ID is required")

    current_date = utils.getdate()

    result = frappe.db.sql(
        """
        SELECT pe.name, pe.student_name, pe.year_group, pe.academic_year, pe.academic_term
        FROM `tabProgram Enrollment` pe
        JOIN `tabAcademic Term` at ON pe.academic_term = at.name
        WHERE pe.student = %s
        AND at.term_start_date > %s
        ORDER BY at.term_start_date ASC
    """,
        (student, current_date),
        as_dict=True,
    )

    return result or None


def update_program_enrollment_status():
    now_date = utils.getdate()
    doc_updates = {}

    ProgramEnrollment = frappe.qb.DocType("Program Enrollment")
    AcademicTerm = frappe.qb.DocType("Academic Term")

    pes_to_update = (
        frappe.qb.from_(ProgramEnrollment)
        .join(AcademicTerm)
        .on(AcademicTerm.name == ProgramEnrollment.academic_term)
        .select(
            ProgramEnrollment.name,
            ProgramEnrollment.status,
            AcademicTerm.term_start_date,
            AcademicTerm.term_end_date,
        )
        .where(
            (
                (ProgramEnrollment.status != "Upcoming")
                & (AcademicTerm.term_start_date > now_date)
            )
            | (
                (ProgramEnrollment.status != "Active")
                & (AcademicTerm.term_start_date < now_date)
                & (AcademicTerm.term_end_date > now_date)
            )
            | (
                (ProgramEnrollment.status != "Expired")
                & (AcademicTerm.term_end_date < now_date)
            )
        )
        .run(as_dict=True)
    )

    for pe_to_update in pes_to_update:
        update = {"status": "Active"}

        if utils.getdate(pe_to_update.term_start_date) > now_date:
            update = {"status": "Upcoming"}
        elif utils.getdate(pe_to_update.term_end_date) < now_date:
            update = {"status": "Expired"}

        doc_updates[pe_to_update.name] = update

    frappe.db.bulk_update("Program Enrollment", doc_updates)
    frappe.db.commit()
