from app.dal.models import Grade, ExamGrade, Subject


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

    def is_debt(self, grade: Grade | None) -> bool:
        return grade is None or grade.is_debt()

    def assigned_results(self, student) -> list[tuple[Subject, Grade | None]]:

        subjects_by_id = {
            subject.id: subject
            for subject in student.group.subjects
        }
        grades_by_subject = {
            grade.subject_id: grade
            for grade in student.grades
        }

        for grade in student.grades:
            subjects_by_id.setdefault(grade.subject_id, grade.subject)

        subjects = sorted(
            subjects_by_id.values(),
            key=lambda subject: (subject.name.casefold(), subject.id),
        )
        return [
            (subject, grades_by_subject.get(subject.id))
            for subject in subjects
        ]

    def debts(self, grades: list[Grade]) -> list[Grade]:
        return [grade for grade in grades if self.is_debt(grade)]
