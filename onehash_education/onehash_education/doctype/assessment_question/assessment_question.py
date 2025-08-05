# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

QUESTION_TYPES = {
    "INTEGER": "Integer",
    "FLOAT": "Float",
    "BOOLEAN": "Boolean",
    "DATE": "Date",
    "HEADING": "Heading",
    "SINGLE_CHOICE": "Single Choice",
    "MULTIPLE_CHOICE": "Multiple Choice",
    "ONE_WORD": "One Word",
    "ONE_LINE": "One Line",
    "SHORT_ANSWER": "Short Answer",
    "LONG_ANSWER": "Long Answer",
}


class AssessmentQuestion(Document):

    def validate(self):
        pass

    def get_correct_options(self):
        return [
            option for option in self.get("options") or [] if option.get("is_correct")
        ]
