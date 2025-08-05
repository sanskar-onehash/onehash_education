import frappe
from onehash_education.onehash_education.doctype.assessment_question.assessment_question import (
    QUESTION_TYPES,
)

# QUESTION_TYPES = {
#     "INTEGER": "Integer",
#     "FLOAT": "Float",
#     "BOOLEAN": "Boolean",
#     "DATE": "Date",
#     "HEADING": "Heading",
#     "SINGLE_CHOICE": "Single Choice",
#     "MULTIPLE_CHOICE": "Multiple Choice",
#     "ONE_WORD": "One Word",
#     "ONE_LINE": "One Line",
#     "SHORT_ANSWER": "Short Answer",
#     "LONG_ANSWER": "Long Answer",
# }


def get_context(context):
    assessment_name = frappe.request.args.get("assessment")

    if not assessment_name or not frappe.db.exists(
        "Assessment",
        {
            "name": assessment_name,
            "is_internal": True,
            "assessment_for": frappe.session.user,
        },
    ):
        context.error = "No assessment found"
        return

    build_assessment_context(context, assessment_name)


def build_assessment_context(context, assessment_name: str) -> None:
    assessment_doc = frappe.get_doc("Assessment", assessment_name)
    assessment_master = frappe.get_doc(
        "Assessment Master", assessment_doc.assessment_master
    )

    # Pagination params
    page = int(frappe.request.args.get("page", 1))
    page_size = int(frappe.request.args.get("page_size", 1))

    grouped_questions = []
    pre_heading_questions = []
    current_group = None
    found_first_heading = False

    for qref in assessment_master.questions:
        question_doc = frappe.get_doc("Assessment Question", qref.question_link)
        q_type = question_doc.question_type

        question_data = {
            "question": question_doc.question,
            "question_type": q_type,
        }

        if q_type in {
            QUESTION_TYPES["SINGLE_CHOICE"],
            QUESTION_TYPES["MULTIPLE_CHOICE"],
        }:
            question_data["options"] = [opt.option for opt in question_doc.options]

        if q_type == QUESTION_TYPES["HEADING"]:
            if not found_first_heading:
                # If there are pre-heading questions, add them as their own group
                if pre_heading_questions:
                    grouped_questions.append(
                        {"heading": None, "questions": pre_heading_questions[:]}
                    )
                # Now start a new group for the heading
                current_group = {"heading": question_doc.question, "questions": []}
                grouped_questions.append(current_group)
                found_first_heading = True
            else:
                # For subsequent headings, start a new group
                current_group = {"heading": question_doc.question, "questions": []}
                grouped_questions.append(current_group)
            continue  # Don't add heading itself as a question

        # Add questions to the current group or pre-heading list
        if not found_first_heading:
            pre_heading_questions.append(question_data)
        else:
            if current_group is not None:
                current_group["questions"].append(question_data)

    # Edge case: If no headings at all, put all questions in one group
    if not found_first_heading and pre_heading_questions:
        grouped_questions.append({"heading": None, "questions": pre_heading_questions})

    context.title = assessment_master.title
    context.grouped_questions = grouped_questions
