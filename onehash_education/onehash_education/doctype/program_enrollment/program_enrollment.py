# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe import utils
from frappe.model.document import Document


class ProgramEnrollment(Document):
    def validate(self):
        self.set_student_name()
        self.validate_duplication()

    def before_save(self):
        self.set_status()

    def before_submit(self):
        self.set_status()

    def set_student_name(self):
        if not self.student_name:
            self.student_name = frappe.db.get_value(
                "Student", self.student, "student_name"
            )

    def set_status(self):
        current_date = utils.getdate()
        academic_year_doc = frappe.get_doc("Academic Year", self.academic_year)

        if academic_year_doc.year_start_date > current_date:
            self.status = "Upcoming"
        elif academic_year_doc.year_end_date < current_date:
            self.status = "Expired"
        else:
            self.status = "Active"

    def validate_duplication(self):
        enrollment = frappe.db.exists(
            "Program Enrollment",
            {
                "student": self.student,
                "program": self.program,
                "academic_year": self.academic_year,
                "academic_term": self.academic_term,
                "docstatus": ("<", 2),
                "name": ("!=", self.name),
            },
        )
        if enrollment:
            frappe.throw(frappe._("Student is already enrolled."))


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


def update_program_enrollment_status():
    now_date = utils.getdate()
    doc_updates = {}

    ProgramEnrollment = frappe.qb.DocType("Program Enrollment")
    AcademicYear = frappe.qb.DocType("Academic Year")

    pes_to_update = (
        frappe.qb.from_(ProgramEnrollment)
        .join(AcademicYear)
        .on(AcademicYear.name == ProgramEnrollment.academic_year)
        .select(
            ProgramEnrollment.name,
            ProgramEnrollment.status,
            AcademicYear.year_start_date,
            AcademicYear.year_end_date,
        )
        .where(
            (
                (ProgramEnrollment.status != "Upcoming")
                & (AcademicYear.year_start_date > now_date)
            )
            | (
                (ProgramEnrollment.status != "Active")
                & (AcademicYear.year_start_date < now_date)
                & (AcademicYear.year_end_date > now_date)
            )
            | (
                (ProgramEnrollment.status != "Expired")
                & (AcademicYear.year_end_date < now_date)
            )
        )
        .run(as_dict=True)
    )

    for pe_to_update in pes_to_update:
        update = {"status": "Active"}

        if utils.getdate(pe_to_update.year_start_date) > now_date:
            update = {"status": "Upcoming"}
        elif utils.getdate(pe_to_update.year_end_date) < now_date:
            update = {"status": "Expired"}

        doc_updates[pe_to_update.name] = update

    frappe.db.bulk_update("Program Enrollment", doc_updates)
    frappe.db.commit()
