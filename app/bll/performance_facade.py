
from app.bll.grade_service import GradeService
from app.bll.grade_calculator import GradeCalculator


class PerformanceFacade:

    def __init__(self):
        self._grades = GradeService()
        self._calc = GradeCalculator()

    def summary(self, student_id: int) -> dict:
        grades = self._grades.for_student(student_id)

        average = self._calc.average(grades)
        debts = self._calc.debts(grades)

        return {
            "student_id": student_id,
            "grade_count": len(grades),
            "average": average,
            "debt_count": len(debts),
            "has_debt": bool(debts),
            "debts": [
                {
                    "subject_id": grade.subject_id,
                    "subject_name": grade.subject.name,
                    "kind": grade.kind
                }
                for grade in debts
            ]
        }
