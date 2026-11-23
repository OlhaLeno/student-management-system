from abc import ABC, abstractmethod

from app.dal.models import Grade, Student, Teacher, AcademicGroup
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
        calc = GradeCalculator()
        group_query = db.session.query(AcademicGroup).order_by(AcademicGroup.name)

        group_id = filters.get("group_id")
        if group_id is not None:
            group_query = group_query.filter(AcademicGroup.id == group_id)

        course = filters.get("course")
        if course is not None:
            group_query = group_query.filter(AcademicGroup.course == course)

        group_results = []
        courses = {}

        for group in group_query.all():
            if not group.students or not group.subjects:
                continue

            group_grades = []
            group_debt_count = 0

            for student in group.students:
                for _, grade in calc.assigned_results(student):
                    if calc.is_debt(grade):
                        group_debt_count += 1
                    if grade is not None:
                        group_grades.append(grade)

            group_results.append({
                "group_id": group.id,
                "group_name": group.name,
                "course": group.course,
                "average": calc.average(group_grades),
                "debt_count": group_debt_count,
            })

            course_data = courses.setdefault(
                group.course,
                {"grades": [], "debt_count": 0},
            )
            course_data["grades"].extend(group_grades)
            course_data["debt_count"] += group_debt_count

        course_results = [
            {
                "course": course_number,
                "average": calc.average(data["grades"]),
                "debt_count": data["debt_count"],
            }
            for course_number, data in sorted(courses.items())
        ]

        return {
            "groups": group_results,
            "courses": course_results,
        }


class TeacherReport(ReportStrategy):

    def generate(
        self,
        grades: list[Grade],
        filters: dict
    ) -> dict:
        teacher_query = db.session.query(Teacher).order_by(Teacher.full_name)
        teacher_id = filters.get("teacher_id")
        if teacher_id is not None:
            teacher_query = teacher_query.filter(Teacher.id == teacher_id)

        teachers = teacher_query.all()
        grades_by_student_subject = {
            (grade.student_id, grade.subject_id): grade
            for grade in grades
        }

        results = []

        for teacher in teachers:
            for subject in sorted(teacher.subjects, key=lambda item: item.name.casefold()):
                groups = sorted(subject.groups, key=lambda item: item.name.casefold())
                if not groups:
                    continue

                students = [student for group in groups for student in group.students]
                exam_scores = []
                passed_count = 0
                failed_count = 0

                for student in students:
                    grade = grades_by_student_subject.get((student.id, subject.id))

                    if grade is None:
                        failed_count += 1
                        continue

                    if grade.kind == "exam":
                        score = grade.score
                        if score is None:
                            failed_count += 1
                            continue

                        exam_scores.append(score)
                        if score >= 51:
                            passed_count += 1
                        else:
                            failed_count += 1

                    elif grade.kind == "credit":
                        if grade.passed is True:
                            passed_count += 1
                        else:
                            failed_count += 1
                    else:
                        failed_count += 1

                average = (
                    sum(exam_scores) / len(exam_scores)
                    if exam_scores else None
                )

                results.append({
                    "teacher_id": teacher.id,
                    "teacher_name": teacher.full_name,
                    "subject_id": subject.id,
                    "subject_name": subject.name,
                    "average": average,
                    "passed_count": passed_count,
                    "failed_count": failed_count,
                })

        return {"teachers": results}


class DebtReport(ReportStrategy):

    def generate(
        self,
        grades: list[Grade],
        filters: dict
    ) -> dict:
        calc = GradeCalculator()
        grades_by_student_subject = {
            (grade.student_id, grade.subject_id): grade
            for grade in grades
        }

        group_query = db.session.query(AcademicGroup).order_by(AcademicGroup.name)
        group_id = filters.get("group_id")
        if group_id is not None:
            group_query = group_query.filter(AcademicGroup.id == group_id)

        course = filters.get("course")
        if course is not None:
            group_query = group_query.filter(AcademicGroup.course == course)

        student_id = filters.get("student_id")
        teacher_id = filters.get("teacher_id")
        results = []

        for group in group_query.all():
            for student in sorted(group.students, key=lambda item: item.full_name.casefold()):
                if student_id is not None and student.id != student_id:
                    continue

                for subject, _ in calc.assigned_results(student):
                    if teacher_id is not None and subject.teacher_id != teacher_id:
                        continue

                    grade = grades_by_student_subject.get((student.id, subject.id))
                    if not calc.is_debt(grade):
                        continue

                    if grade is None:
                        kind = None
                        result = "Не складено"
                    elif grade.kind == "exam":
                        kind = grade.kind
                        result = grade.score if grade.score is not None else "Не складено"
                    else:
                        kind = grade.kind
                        result = "Не зараховано"

                    results.append({
                        "student_id": student.id,
                        "student_name": student.full_name,
                        "group_name": group.name,
                        "course": group.course,
                        "subject_name": subject.name,
                        "teacher_name": subject.teacher.full_name,
                        "kind": kind,
                        "result": result,
                    })

        return {
            "debt_count": len(results),
            "debts": results,
        }


class StudentReport(ReportStrategy):

    def generate(self, grades: list[Grade], filters: dict) -> dict:
        student_id = filters.get("student_id")
        if type(student_id) is not int or student_id <= 0:
            raise ValueError("Оберіть студента для формування звіту.")

        student = db.session.get(Student, student_id)
        if student is None:
            raise LookupError("Студента не знайдено.")

        calc = GradeCalculator()
        assigned_results = calc.assigned_results(student)
        student_grades = [grade for _, grade in assigned_results if grade is not None]

        results = []
        for subject, grade in assigned_results:
            if grade is None:
                results.append({
                    "subject_name": subject.name,
                    "teacher_name": subject.teacher.full_name,
                    "kind": None,
                    "kind_name": "—",
                    "result": "Не складено",
                    "has_debt": True,
                })
                continue

            is_exam = grade.kind == "exam"
            results.append({
                "subject_name": subject.name,
                "teacher_name": subject.teacher.full_name,
                "kind": grade.kind,
                "kind_name": "Іспит" if is_exam else "Залік",
                "result": (
                    grade.score if grade.score is not None else "Не складено"
                ) if is_exam else (
                    "Зараховано" if grade.passed is True else "Не зараховано"
                ),
                "has_debt": calc.is_debt(grade),
            })

        return {
            "student_id": student.id,
            "student_name": student.full_name,
            "group_name": student.group.name,
            "course": student.group.course,
            "average": calc.average(student_grades),
            "grade_count": len(student_grades),
            "debt_count": sum(1 for _, grade in assigned_results if calc.is_debt(grade)),
            "subjects": results,
        }
