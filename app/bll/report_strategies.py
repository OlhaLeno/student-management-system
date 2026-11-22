from abc import ABC, abstractmethod

from app.dal.models import Grade, Student
from app.dal.database import db
from app.bll.grade_calculator import GradeCalculator


class ReportStrategy(ABC):

    @abstractmethod
    def generate(
        self,
        grades: list[Grade],
        filters: dict
    ) -> dict:
        pass


class GroupReport(ReportStrategy):

    def generate(
        self,
        grades: list[Grade],
        filters: dict
    ) -> dict:

        groups = {}
        courses = {}
        calc = GradeCalculator()

        for grade in grades:
            group = grade.student.group

            if "group_id" in filters:
                if group.id != filters["group_id"]:
                    continue

            if "course" in filters:
                if group.course != filters["course"]:
                    continue

            groups.setdefault(group.id, []).append(grade)
            courses.setdefault(group.course, []).append(grade)

        group_results = []

        for group_id, items in groups.items():
            group = items[0].student.group

            group_results.append({
                "group_id": group_id,
                "group_name": group.name,
                "course": group.course,
                "average": calc.average(items),
                "debt_count": len(calc.debts(items))
            })

        course_results = []

        for course, items in sorted(courses.items()):
            course_results.append({
                "course": course,
                "average": calc.average(items),
                "debt_count": len(calc.debts(items))
            })

        return {
            "groups": group_results,
            "courses": course_results
        }


class TeacherReport(ReportStrategy):

    def generate(
        self,
        grades: list[Grade],
        filters: dict
    ) -> dict:

        teachers = {}
        calc = GradeCalculator()

        for grade in grades:
            teacher = grade.subject.teacher

            if "teacher_id" in filters:
                if teacher.id != filters["teacher_id"]:
                    continue

            teachers.setdefault(teacher.id, []).append(grade)

        results = []

        for teacher_id, items in teachers.items():
            teacher = items[0].subject.teacher

            results.append({
                "teacher_id": teacher_id,
                "teacher_name": teacher.full_name,
                "average": calc.average(items),
                "grade_count": len(items)
            })

        return {
            "teachers": results
        }



class DebtReport(ReportStrategy):

    def generate(
        self,
        grades: list[Grade],
        filters: dict
    ) -> dict:

        calc = GradeCalculator()
        debts = calc.debts(grades)

        results = []

        for grade in debts:
            student = grade.student
            group = student.group
            subject = grade.subject

            if "group_id" in filters:
                if group.id != filters["group_id"]:
                    continue

            if "course" in filters:
                if group.course != filters["course"]:
                    continue

            if "student_id" in filters:
                if student.id != filters["student_id"]:
                    continue

            if "teacher_id" in filters:
                if subject.teacher_id != filters["teacher_id"]:
                    continue

            results.append({
                "student_id": student.id,
                "student_name": student.full_name,
                "group_name": group.name,
                "course": group.course,
                "subject_name": subject.name,
                "teacher_name": subject.teacher.full_name,
                "kind": grade.kind,
                "result": grade.score if grade.kind == "exam"
                          else "Не зараховано"
            })

        return {
            "debt_count": len(results),
            "debts": results
        }


class StudentReport(ReportStrategy):
    """Повна успішність одного студента за призначеними його групі дисциплінами."""

    def generate(self, grades: list[Grade], filters: dict) -> dict:
        student_id = filters.get("student_id")
        if type(student_id) is not int or student_id <= 0:
            raise ValueError("Оберіть студента для формування звіту.")

        student = db.session.get(Student, student_id)
        if student is None:
            raise LookupError("Студента не знайдено.")

        student_grades = [g for g in grades if g.student_id == student_id]
        grades_by_subject = {g.subject_id: g for g in student_grades}

        subjects_by_id = {subject.id: subject for subject in student.group.subjects}
        for grade in student_grades:
            subjects_by_id[grade.subject_id] = grade.subject

        results = []
        for subject in sorted(subjects_by_id.values(), key=lambda s: s.name.casefold()):
            grade = grades_by_subject.get(subject.id)
            if grade is None:
                results.append({
                    "subject_name": subject.name,
                    "teacher_name": subject.teacher.full_name,
                    "kind": None,
                    "kind_name": "—",
                    "result": "Не внесено",
                    "has_debt": None,
                })
            else:
                is_exam = grade.kind == "exam"
                results.append({
                    "subject_name": subject.name,
                    "teacher_name": subject.teacher.full_name,
                    "kind": grade.kind,
                    "kind_name": "Іспит" if is_exam else "Залік",
                    "result": grade.score if is_exam else (
                        "Зараховано" if grade.passed else "Не зараховано"
                    ),
                    "has_debt": grade.is_debt(),
                })

        calc = GradeCalculator()
        return {
            "student_id": student.id,
            "student_name": student.full_name,
            "group_name": student.group.name,
            "course": student.group.course,
            "average": calc.average(student_grades),
            "grade_count": len(student_grades),
            "debt_count": len(calc.debts(student_grades)),
            "pending_count": sum(r["has_debt"] is None for r in results),
            "subjects": results,
        }
