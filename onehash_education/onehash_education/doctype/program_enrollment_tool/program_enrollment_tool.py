# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.safe_exec import call_whitelisted_function


class ProgramEnrollmentTool(Document):
    @frappe.whitelist()
    def get_students(self):
        students = []

        if not self.get_students_from:
            frappe.throw(_("Mandatory field - Get Students From"))
        elif not self.year_group:
            frappe.throw(_("Mandatory field - Year Group"))
        elif not self.academic_year:
            frappe.throw(_("Mandatory field - Academic Year"))
        elif self.acadmic_term:
            frappe.get_doc("Acadmic Term", self.academic_term).validate_term_date_range(
                self.academic_year
            )

        if self.get_students_from == "Student Applicant":
            students = frappe.db.sql(
                """select name as student_applicant, applicant_name as student_name from `tabStudent Applicant`
                where enrolled=0 and year_group=%(year_group)s and academic_year=%(academic_year)s""",
                self.as_dict(),
                as_dict=1,
            )
        elif self.get_students_from == "Program Enrollment":
            AcademicTerms = frappe.qb.DocType("Academic Terms")
            ProgramEnrollment = frappe.qb.DocType("Program Enrollment")
            Student = frappe.qb.DocType("Student")

            students = (
                frappe.qb.from_(ProgramEnrollment)
                .join(AcademicTerms)
                .on(AcademicTerms.parent == ProgramEnrollment.name)
                .join(Student)
                .on(Student.name == ProgramEnrollment.student)
                .where(
                    (ProgramEnrollment.year_group == self.year_group)
                    & (ProgramEnrollment.academic_year == self.academic_year)
                    & (ProgramEnrollment.docstatus != 2)
                    & (AcademicTerms.academic_term == self.academic_term)
                    & (Student.enabled == 1)
                )
                .select(ProgramEnrollment.student, ProgramEnrollment.student_name)
            ).run(as_dict=True)

        if students:
            return students
        else:
            frappe.throw(_("No students Found"))

    @frappe.whitelist()
    def enroll_students(self):
        if not self.students:
            frappe.throw("No Students found to enroll.")
        if not self.new_academic_terms:
            frappe.throw("No Academic Term found to enroll in.")

        total = len(self.students)
        for i, student in enumerate(self.students):
            frappe.publish_realtime(
                "program_enrollment_tool",
                dict(progress=[i + 1, total]),
                user=frappe.session.user,
            )
            if student.student:
                if not self.new_academic_year:
                    frappe.throw("New Academic Year is required.")

                prog_enrollment = frappe.new_doc("Program Enrollment")
                prog_enrollment.student = student.student
                prog_enrollment.student_name = student.student_name
                prog_enrollment.year_group = self.new_year_group
                prog_enrollment.academic_year = self.new_academic_year
                for academic_term in self.new_academic_terms or []:
                    prog_enrollment.append(
                        "academic_terms", {"academic_term": academic_term.academic_term}
                    )
                prog_enrollment.enrollment_date = self.enrollment_date

                prog_enrollment.save()
            elif student.student_applicant:
                call_whitelisted_function(
                    "onehash_education.api.enroll_student",
                    applicant_name=student.student_applicant,
                    terms=[term.academic_term for term in self.new_academic_terms],
                )

                for program_enrolled in frappe.response["message"]:
                    prog_enrollment = frappe.get_doc(
                        "Program Enrollment", program_enrolled
                    )
                    prog_enrollment.academic_year = self.academic_year
                    prog_enrollment.enrollment_date = self.enrollment_date
                    prog_enrollment.save()
        frappe.msgprint(_("{0} Students have been enrolled").format(total))
        frappe.response["message"] = "success"
