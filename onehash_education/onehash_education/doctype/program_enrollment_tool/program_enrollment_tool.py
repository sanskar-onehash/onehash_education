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
        else:
            condition = (
                "and academic_term=%(academic_term)s" if self.academic_term else " "
            )
            if self.get_students_from == "Student Applicant":
                students = frappe.db.sql(
                    """select name as student_applicant, applicant_name as student_name from `tabStudent Applicant`
					where enrolled=0 and year_group=%(year_group)s and academic_year=%(academic_year)s {0}""".format(
                        condition
                    ),
                    self.as_dict(),
                    as_dict=1,
                )
            elif self.get_students_from == "Program Enrollment":
                students = frappe.db.sql(
                    """select student, student_name from `tabProgram Enrollment`
					where year_group=%(year_group)s and academic_year=%(academic_year)s {0} and docstatus != 2""".format(
                        condition
                    ),
                    self.as_dict(),
                    as_dict=1,
                )

                student_list = [d.student for d in students]
                if student_list:
                    inactive_students = frappe.db.sql(
                        """
						select name as student, student_name from `tabStudent` where name in (%s) and enabled = 0"""
                        % ", ".join(["%s"] * len(student_list)),
                        tuple(student_list),
                        as_dict=1,
                    )

                    for student in students:
                        if student.student in [d.student for d in inactive_students]:
                            students.remove(student)

        if students:
            return students
        else:
            frappe.throw(_("No students Found"))

    @frappe.whitelist()
    def enroll_students(self):
        total = len(self.students)
        for i, student in enumerate(self.students):
            frappe.publish_realtime(
                "program_enrollment_tool",
                dict(progress=[i + 1, total]),
                user=frappe.session.user,
            )
            if student.student:
                prog_enrollment = frappe.new_doc("Program Enrollment")
                prog_enrollment.student = student.student
                prog_enrollment.student_name = student.student_name
                prog_enrollment.year_group = self.new_year_group
                prog_enrollment.academic_year = self.new_academic_year
                prog_enrollment.academic_term = self.new_academic_term
                prog_enrollment.save()
            elif student.student_applicant:
                call_whitelisted_function(
                    "onehash_education.api.enroll_student",
                    applicant_name=student.student_applicant,
                )
                prog_enrollment = frappe.get_doc(
                    "Program Enrollment", frappe.response["message"]
                )

                prog_enrollment.academic_year = self.academic_year
                prog_enrollment.academic_term = self.academic_term
                prog_enrollment.save()
        frappe.msgprint(_("{0} Students have been enrolled").format(total))
        frappe.response["message"] = "success"
