
from app.dal.models import Grade, ExamGrade


class GradeCalculator:

    def average(self, grades: list[Grade]) -> float | None:
        exam_scores = [
            grade.score
            for grade in grades
            if isinstance(grade, ExamGrade) and grade.score is not None
        ]

        if not exam_scores:
            return None

        return sum(exam_scores) / len(exam_scores)

    def debts(self, grades: list[Grade]) -> list[Grade]:
        return [
            grade
            for grade in grades
            if grade.is_debt()
        ]
