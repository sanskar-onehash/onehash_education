# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

QUESTION_TYPES = {
    "INTEGER": "Integer",
    "FLOAT": "Float",
    "BOOLEAN": "Boolean",
    "DATE": "Date",
    "SINGLE_CHOICE": "Single Choice",
    "MULTIPLE_CHOICE": "Multiple Choice",
    "ONE_WORD": "One Word",
    "SHORT_ANSWER": "Short Answer",
    "LONG_ANSWER": "Long Answer",
}


class AssessmentQuestion(Document):

    def validate(self):
        self.validate_question_type()

    def get_correct_options(self):
        return [
            option for option in self.get("options") or [] if option.get("is_correct")
        ]

    def validate_question_type(self):
        question_type = self.get("question_type")

        if (
            question_type == QUESTION_TYPES["SINGLE_CHOICE"]
            or question_type == QUESTION_TYPES["MULTIPLE_CHOICE"]
        ):
            correct_options = len(self.get_correct_options())

            if not correct_options:
                frappe.throw("Atleast one correct option is required")

            if (
                question_type == QUESTION_TYPES["MULTIPLE_CHOICE"]
                and correct_options < 2
            ):
                frappe.throw("Select `Single Choice` or add another correct option.")

            if question_type == QUESTION_TYPES["SINGLE_CHOICE"] and correct_options > 1:
                frappe.throw("Only one correct option is allowed.")
