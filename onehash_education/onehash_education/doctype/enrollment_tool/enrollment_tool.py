# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils.safe_exec import call_whitelisted_function


class EnrollmentTool(Document):
    @frappe.whitelist()
    def get_students(self):
        students = []

        if not self.get_students_from:
            frappe.throw(_("Mandatory field - Get Students From"))
        elif not self.year_group:
            frappe.throw(_("Mandatory field - Year Group"))
        elif not self.academic_year:
            frappe.throw(_("Mandatory field - Academic Year"))
        elif self.academic_term:
            frappe.get_doc(
                "Academic Term", self.academic_term
            ).validate_term_date_range(self.academic_year)

        if self.get_students_from == "Student Applicant":
            students = frappe.db.sql(
                """select name as student_applicant, applicant_name as student_name from `tabStudent Applicant`
                where enrolled=0 and year_group=%(year_group)s and academic_year=%(academic_year)s""",
                self.as_dict(),
                as_dict=1,
            )
        elif self.get_students_from == "Enrollment":
            if not self.academic_term:
                frappe.throw(_("Mandatory field - Academic Term"))

            Enrollment = frappe.qb.DocType("Enrollment")
            Student = frappe.qb.DocType("Student")

            enrollment_conditions = (
                (Enrollment.year_group == self.year_group)
                & (Enrollment.academic_year == self.academic_year)
                & (Enrollment.docstatus == 1)
                & (Enrollment.academic_term == self.academic_term)
                & (Student.enabled == 1)
                & (Enrollment.status != "Expired")
            )
            if self.active_enrollments:
                enrollment_conditions = enrollment_conditions & (
                    Enrollment.status == "Active"
                )

            students = (
                frappe.qb.from_(Enrollment)
                .join(Student)
                .on(Student.name == Enrollment.student)
                .where(enrollment_conditions)
                .select(Enrollment.student, Enrollment.student_name)
            ).run(as_dict=True)

            seen_students = set()
            unique_students = [
                student
                for student in students
                if (student_id := student.get("student")) not in seen_students
                and not seen_students.add(student_id)
            ]

            if not unique_students:
                frappe.throw(_("No students Found"))

            return unique_students

    @frappe.whitelist()
    def enroll_students(self):
        if not self.students:
            frappe.throw("No Students found to enroll.")
        if not self.new_academic_terms:
            frappe.throw("No Academic Term found to enroll in.")

        standard_fields = (
            [field.get("fieldname") for field in frappe.model.std_fields]
            + list(frappe.model.child_table_fields)
            + ["amended_from"]
        )

        history_doc = frappe.new_doc("Enrollment History")
        for key, value in self.as_dict().items():
            if key in standard_fields:
                continue
            if not history_doc.meta.has_field(key):
                continue

            if isinstance(value, list):
                for row in value:
                    history_doc.append(key, row)
            else:
                history_doc.set(key, value)
        history_doc = history_doc.insert(ignore_permissions=True)

        total = len(self.students)
        for i, student in enumerate(self.students):
            frappe.publish_realtime(
                "enrollment_tool",
                dict(progress=[i + 1, total]),
                user=frappe.session.user,
            )
            if student.student:
                if not self.new_academic_year:
                    frappe.throw("New Academic Year is required.")

                for new_academic_term in self.new_academic_terms or []:
                    enrollment = frappe.new_doc("Enrollment")
                    enrollment.update(
                        {
                            "student": student.student,
                            "student_name": student.student_name,
                            "year_group": self.new_year_group,
                            "academic_year": self.new_academic_year,
                            "academic_term": new_academic_term.academic_term,
                            "enrollment_date": self.enrollment_date,
                        }
                    )
                    enrollment.save()
            elif student.student_applicant:
                call_whitelisted_function(
                    "onehash_education.api.enroll_student",
                    applicant_name=student.student_applicant,
                    terms=[term.academic_term for term in self.new_academic_terms],
                    history_docname=history_doc.name,
                )

                for enrolled in frappe.response["message"]:
                    enrollment = frappe.get_doc("Enrollment", enrolled)
                    enrollment.academic_year = self.academic_year
                    enrollment.enrollment_date = self.enrollment_date
                    enrollment.created_by_enrollment_tool = True
                    enrollment.enrollment_source = history_doc.name
                    enrollment.save()
        frappe.msgprint(
            _(f"{total} Student{'s have' if total > 1 else 'has'} been enrolled")
        )
        frappe.response["message"] = "success"
