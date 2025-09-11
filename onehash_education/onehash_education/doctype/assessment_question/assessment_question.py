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

    def get_correct_answer(self):
        if self.question_type == QUESTION_TYPES["INTEGER"]:
            return self.answer_int

        if self.question_type == QUESTION_TYPES["FLOAT"]:
            return self.answer_float

        if self.question_type == QUESTION_TYPES["BOOLEAN"] and self.answer_boolean:
            return True if self.answer_boolean == "True" else False

        if self.question_type == QUESTION_TYPES["DATE"] and self.answer_date:
            return frappe.utils.getdate(self.answer_date)

        if self.question_type in [
            QUESTION_TYPES["SINGLE_CHOICE"],
            QUESTION_TYPES["MULTIPLE_CHOICE"],
        ]:
            return [
                option.get("option")
                for option in self.get("options") or []
                if option.get("is_correct")
            ]

        if self.question_type == QUESTION_TYPES["ONE_WORD"] and self.answer_one_word:
            return self.answer_one_word

        return None
