from app.bll.grade_service import GradeService
from app.bll.grade_calculator import GradeCalculator
from app.bll.student_service import StudentService


class PerformanceFacade:

    def __init__(self):
        self._grades = GradeService()
        self._students = StudentService()
        self._calc = GradeCalculator()

    def summary(self, student_id: int) -> dict:
        student = self._students.get_by_id(student_id)
        grades = self._grades.for_student(student_id)
        assigned_results = self._calc.assigned_results(student)
        debts = [
            (subject, grade)
            for subject, grade in assigned_results
            if self._calc.is_debt(grade)
        ]

        return {
            "student_id": student_id,
            "grade_count": len(grades),
            "average": self._calc.average(grades),
            "debt_count": len(debts),
            "has_debt": bool(debts),
            "debts": [
                {
                    "subject_id": subject.id,
                    "subject_name": subject.name,
                    "kind": grade.kind if grade is not None else None,
                }
                for subject, grade in debts
            ],
        }
