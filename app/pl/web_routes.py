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
from app.bll.performance_facade import PerformanceFacade
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
    students = [student_to_dict(s) for s in StudentService().get_all()]
    subjects = [subject_to_dict(s) for s in SubjectService().get_all()]
    student_id = request.args.get('student_id', type=int)
    selected = next((s for s in students if s['id'] == student_id), None)
    service = GradeService()
    if selected:
        records = service.for_student(student_id)
        summary = PerformanceFacade().summary(student_id)
    else:
        records = service.all_grades()
        summary = None
    return render_template('grades.html', students=students, subjects=subjects,
                           grades=[grade_to_dict(g) for g in records],
                           selected=selected, summary=summary)


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
