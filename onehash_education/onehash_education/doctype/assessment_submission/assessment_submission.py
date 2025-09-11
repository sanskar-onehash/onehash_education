# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssessmentSubmission(Document):
    def before_save(self):
        self.calculate_correct_answers()

    def calculate_correct_answers(self):
        self.correct_answers = 0
        for submitted_answer in self.submitted_answers:
            if submitted_answer.is_correct:
                self.correct_answers = self.correct_answers + 1


def create_assessment_submission(assessment_master, answers, ignore_permissions=False):
    if isinstance(assessment_master, str):
        assessment_master = frappe.get_doc("Assessment Master", assessment_master)
    if not assessment_master:
        frappe.throw("Assessment Master is required")

    correct_answers_by_questions = {}
    for qref in assessment_master.questions:
        question_doc = frappe.get_doc("Assessment Question", qref.question_link)
        correct_answers_by_questions[question_doc.name] = (
            question_doc.get_correct_answer()
        )

    result = []
    correct_answers_count = 0
    for question_name, user_answer in answers.items():
        if not question_name or question_name not in correct_answers_by_questions:
            frappe.throw(f"Invalid or missing question in answer: {user_answer}")

        correct_answer = correct_answers_by_questions[question_name]

        is_correct = compare_answers(correct_answer, user_answer)

        if is_correct:
            correct_answers_count += 1

        parsed_answer = user_answer

        if isinstance(user_answer, list):
            parsed_answer = ", ".join(user_answer)

        result.append(
            {
                "question": question_name,
                "answer": parsed_answer,
                "is_correct": is_correct,
            }
        )

    return frappe.get_doc(
        {
            "doctype": "Assessment Submission",
            "assessment_master": assessment_master.name,
            "submitted_answers": result,
            "correct_answers": correct_answers_count,
        }
    ).save(ignore_permissions=ignore_permissions)


def compare_answers(correct, user):
    if isinstance(correct, list):
        if not isinstance(user, list):
            user = [user]
        correct_set = set(correct)
        user_set = set(user)
        return correct_set == user_set

    elif isinstance(correct, bool):
        return str(correct).lower() == str(user).lower()

    elif isinstance(correct, (int, float)):
        try:
            return type(correct)(user) == correct
        except:
            return False

    elif isinstance(correct, str):
        return correct.strip().lower() == str(user).strip().lower()

    elif isinstance(correct, frappe.utils.datetime.datetime):
        try:
            if isinstance(user, str):
                user_date = frappe.utils.getdate(user)
                return user_date == correct
        except:
            return False

    return False
