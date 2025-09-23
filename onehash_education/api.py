import frappe


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
def enroll_student(applicant_name):
    frappe.publish_realtime(
        "enroll_student_progress", {"progress": [1, 4]}, user=frappe.session.user
    )
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
    student.save()

    program_enrollment = frappe.new_doc("Program Enrollment")
    program_enrollment.student = student.name
    program_enrollment.student_name = student.student_name
    program_enrollment.year_group = student_applicant.year_group
    program_enrollment.academic_year = student_applicant.academic_year
    program_enrollment.save()

    frappe.db.set_value("Student Applicant", applicant_name, "enrolled", 1)
    frappe.publish_realtime(
        "enroll_student_progress", {"progress": [2, 4]}, user=frappe.session.user
    )

    frappe.response["message"] = program_enrollment.name
