from flask import Blueprint, render_template, request

from app.bll.student_service import StudentService
from app.bll.teaching_service import TeacherService, SubjectService
from app.bll.university_service import (
    InstituteService, SpecialtyService, AcademicGroupService
)
from app.pl.university_routes import institute_to_dict, specialty_to_dict, group_to_dict
from app.pl.student_routes import student_to_dict
from app.pl.teaching_routes import teacher_to_dict, subject_to_dict
from app.bll.schedule_service import ScheduleService
from app.bll.grade_service import GradeService
from app.bll.report_service import ReportService
from app.bll.report_strategies import GroupReport, TeacherReport, DebtReport, StudentReport
from app.pl.schedule_routes import schedule_to_dict
from app.pl.grade_routes import grade_to_dict


web = Blueprint("web", __name__)


@web.get("/")
def index():
    return render_template(
        "index.html",
        student_count=len(StudentService().get_all()),
        teacher_count=len(TeacherService().get_all()),
        group_count=len(AcademicGroupService().get_all()),
        subject_count=len(SubjectService().get_all()),
    )


@web.get("/university")
def university():
    return render_template(
        "university.html",
        institutes=[institute_to_dict(i) for i in InstituteService().get_all()],
        specialties=[specialty_to_dict(s) for s in SpecialtyService().get_all()],
        groups=[group_to_dict(g) for g in AcademicGroupService().get_all()],
    )


@web.get("/students")
def students():
    return render_template(
        "students.html",
        students=[student_to_dict(s) for s in StudentService().get_all()],
        groups=[group_to_dict(g) for g in AcademicGroupService().get_all()],
    )


@web.get("/teachers")
def teachers():
    return render_template(
        "teachers.html",
        teachers=[teacher_to_dict(t) for t in TeacherService().get_all()],
    )


@web.get("/subjects")
def subjects():
    return render_template(
        "subjects.html",
        subjects=[subject_to_dict(s) for s in SubjectService().get_all()],
        teachers=[teacher_to_dict(t) for t in TeacherService().get_all()],
        groups=[group_to_dict(g) for g in AcademicGroupService().get_all()],
    )

@web.get('/schedule')
def schedule():
    groups = [group_to_dict(g) for g in AcademicGroupService().get_all()]
    teachers = [teacher_to_dict(t) for t in TeacherService().get_all()]
    subjects = [subject_to_dict(s) for s in SubjectService().get_all()]
    days = {1: 'Понеділок', 2: 'Вівторок', 3: 'Середа',
            4: 'Четвер', 5: 'П’ятниця'}
    group_id = request.args.get('group_id', type=int)
    teacher_id = request.args.get('teacher_id', type=int)
    day = request.args.get('day', type=int)
    if day not in days:
        day = None
    entries = ScheduleService().get_all(group_id=group_id, day=day,
                                        teacher_id=teacher_id)
    entries = sorted(entries, key=lambda e: (e.day, e.start_time, e.id))
    return render_template('schedule.html', groups=groups, teachers=teachers,
                           subjects=subjects, days=days,
                           entries=[schedule_to_dict(e) for e in entries],
                           group_id=group_id, teacher_id=teacher_id, day=day)


@web.get('/grades')
def grades():
    student_models = StudentService().get_all()
    subject_models = SubjectService().get_all()
    students = [student_to_dict(student) for student in student_models]
    subjects = [subject_to_dict(subject) for subject in subject_models]

    student_id = request.args.get('student_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    requested_group_id = request.args.get('group_id', type=int)
    groups = [group_to_dict(group) for group in AcademicGroupService().get_all()]

    selected_student_model = next(
        (student for student in student_models if student.id == student_id), None
    )
    selected_student = next(
        (student for student in students if student['id'] == student_id), None
    )
    selected_subject_model = next(
        (subject for subject in subject_models if subject.id == subject_id), None
    )
    selected_subject = next(
        (subject for subject in subjects if subject['id'] == subject_id), None
    )

    service = GradeService()
    student_grades = []
    student_summary = None
    subject_students = []
    subject_summary = None
    selected_group = None

    if selected_student_model is not None:
        records = service.for_student(selected_student_model.id)
        grades_by_subject = {grade.subject_id: grade for grade in records}
        assigned_subjects = sorted(
            selected_student_model.group.subjects,
            key=lambda subject: subject.name.casefold()
        )

        for subject in assigned_subjects:
            grade = grades_by_subject.get(subject.id)
            if grade is not None:
                row = grade_to_dict(grade)
            else:
                row = {
                    'id': None,
                    'kind': None,
                    'kind_name': '—',
                    'result': 'Не складено',
                    'has_debt': True,
                    'debt_status': 'Є',
                }
            row['subject_name'] = subject.name
            student_grades.append(row)

        exam_scores = [
            grade.score for grade in records
            if grade.kind == 'exam' and grade.score is not None
        ]
        student_summary = {
            'average': sum(exam_scores) / len(exam_scores) if exam_scores else None,
            'grade_count': len(records),
            'debt_count': sum(1 for row in student_grades if row['has_debt']),
        }

    if selected_subject_model is not None:
        subject_group_models = selected_subject_model.groups
        selected_group_model = next(
            (group for group in subject_group_models if group.id == requested_group_id),
            None,
        )
        if selected_group_model is not None:
            selected_group = next(
                (group for group in groups if group['id'] == selected_group_model.id),
                None,
            )
            assigned_group_ids = {selected_group_model.id}
        else:
            assigned_group_ids = {group.id for group in subject_group_models}

        enrolled_students = [
            student for student in student_models
            if student.group_id in assigned_group_ids
        ]
        enrolled_students.sort(
            key=lambda student: (student.group.name.casefold(), student.full_name.casefold())
        )
        grades_by_student = {
            grade.student_id: grade
            for grade in service.for_subject(selected_subject_model.id)
        }

        for student in enrolled_students:
            grade = grades_by_student.get(student.id)
            if grade is not None:
                row = grade_to_dict(grade)
            else:
                row = {
                    'id': None,
                    'kind': None,
                    'kind_name': '—',
                    'result': 'Не складено',
                    'has_debt': True,
                    'debt_status': 'Є',
                }
            row.update({
                'student_name': student.full_name,
                'group_name': student.group.name,
                'course': student.group.course,
            })
            subject_students.append(row)

        subject_summary = {
            'student_count': len(subject_students),
            'passed_count': sum(1 for row in subject_students if not row['has_debt']),
            'debt_count': sum(1 for row in subject_students if row['has_debt']),
        }

    return render_template(
        'grades.html',
        students=students,
        subjects=subjects,
        groups=groups,
        selected_student=selected_student,
        selected_subject=selected_subject,
        selected_group=selected_group,
        student_grades=student_grades,
        student_summary=student_summary,
        subject_students=subject_students,
        subject_summary=subject_summary,
    )


@web.get('/reports')
def reports():
    groups = [group_to_dict(g) for g in AcademicGroupService().get_all()]
    teachers = [teacher_to_dict(t) for t in TeacherService().get_all()]
    students = [student_to_dict(s) for s in StudentService().get_all()]
    courses = sorted({g['course'] for g in groups})
    filters = {name: request.args.get(name, type=int) for name in
               ('group_id', 'course', 'teacher_id', 'student_id')}
    service = ReportService()
    service.set_strategy(GroupReport())
    group_report = service.generate({k: filters[k] for k in ('group_id', 'course')
                                     if filters[k] is not None})
    service.set_strategy(TeacherReport())
    teacher_report = service.generate({'teacher_id': filters['teacher_id']}
                                      if filters['teacher_id'] is not None else {})
    service.set_strategy(DebtReport())
    debt_report = service.generate({k: filters[k] for k in
                                    ('group_id', 'course', 'student_id', 'teacher_id')
                                    if filters[k] is not None})
    student_report = None
    if filters['student_id'] is not None:
        service.set_strategy(StudentReport())
        student_report = service.generate({'student_id': filters['student_id']})
    return render_template('reports.html', groups=groups, teachers=teachers,
                           students=students, courses=courses, filters=filters,
                           group_report=group_report, teacher_report=teacher_report,
                           debt_report=debt_report, student_report=student_report)
