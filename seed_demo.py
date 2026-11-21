from collections import Counter
from datetime import time

from app import create_app
from app.dal.database import db
from app.dal.models import (
    Institute, Specialty, AcademicGroup, Student, Teacher,
    Subject, Grade, ScheduleEntry,
)
from app.bll.university_service import (
    InstituteService, SpecialtyService, AcademicGroupService,
)
from app.bll.student_service import StudentService
from app.bll.teaching_service import TeacherService, SubjectService
from app.bll.schedule_service import ScheduleService
from app.bll.grade_service import GradeService


INSTITUTES = {
    "ІКТЕ": "Інститут інформаційно-комунікаційних технологій та електронної інженерії",
    "ІКНІ": "Інститут комп'ютерних наук та інформаційних технологій",
    "ІКТА": "Інститут комп'ютерних технологій, автоматики та метрології",
    "ІНЕМ": "Інститут економіки і менеджменту",
    "ІЕСК": "Інститут енергетики та систем керування",
    "ІМІТ": "Інститут механічної інженерії та транспорту",
    "ІАРД": "Інститут архітектури та дизайну",
}

GROUPS = [
    ("ІР-44", 4, "ІКТЕ", "Комп'ютерні науки"),
    ("ІР-34", 3, "ІКТЕ", "Комп'ютерні науки"),
    ("КН-31", 3, "ІКНІ", "Комп'ютерні науки"),
    ("КН-21", 2, "ІКНІ", "Комп'ютерні науки"),
    ("ПЗ-21", 2, "ІКНІ", "Інженерія програмного забезпечення"),
    ("КБ-41", 4, "ІКТА", "Кібербезпека та захист інформації"),
    ("КС-22", 2, "ІКТА", "Комп'ютерна інженерія"),
    ("МЕ-31", 3, "ІНЕМ", "Менеджмент"),
    ("МК-21", 2, "ІНЕМ", "Маркетинг"),
    ("ЕЕ-21", 2, "ІЕСК", "Електроенергетика, електротехніка та електромеханіка"),
    ("АТ-22", 2, "ІМІТ", "Автомобільний транспорт"),
    ("АР-31", 3, "ІАРД", "Архітектура та містобудування"),
]

STUDENTS = {
    "ІР-44": [
        "Гаврилюк Марта Романівна",
        "Леньо Ольга",
        "Данилюк Максим Юрійович",
        "Соломко Юлія Андріївна",
    ],
    "ІР-34": [
        "Клименко Олег Сергійович",
        "Демчук Катерина Ігорівна",
        "Боровик Тарас Васильович",
        "Лазаренко Вікторія Богданівна",
    ],
    "КН-31": [
        "Козак Марія Миколаївна",
        "Остапчук Назар Петрович",
        "Левицька Ірина Володимирівна",
        "Федорчук Андрій Юрійович",
    ],
    "КН-21": [
        "Жук Андрій Романович",
        "Яворська Софія Олегівна",
        "Павлюк Владислав Ігорович",
        "Наконечна Дарина Іванівна",
    ],
    "ПЗ-21": [
        "Ткаченко Максим Олександрович",
        "Стець Олена Ігорівна",
        "Вербицький Артем Романович",
        "Рибак Христина Василівна",
    ],
    "КБ-41": [
        "Дудар Марко Тарасович",
        "Білик Анастасія Андріївна",
        "Шульга Денис Вікторович",
        "Тимчук Аліна Михайлівна",
    ],
    "КС-22": [
        "Гнатишин Роман Петрович",
        "Зозуля Марія Олександрівна",
        "Ковальчук Володимир Ігорович",
        "Яремчук Соломія Назарівна",
    ],
    "МЕ-31": [
        "Боднар Оксана Василівна",
        "Литвин Олексій Сергійович",
        "Кирилюк Юлія Іванівна",
        "Черниш Павло Андрійович",
    ],
    "МК-21": [
        "Олійник Ірина Олегівна",
        "Барановський Дмитро Петрович",
        "Лисенко Вікторія Сергіївна",
        "Гуменюк Богдан Юрійович",
    ],
    "ЕЕ-21": [
        "Горбач Андрій Миколайович",
        "Крамар Софія Василівна",
        "Кравченко Назар Олегович",
        "Мазур Анна Ігорівна",
    ],
    "АТ-22": [
        "Хоменко Олег Вікторович",
        "Вовк Марія Тарасівна",
        "Гавриш Денис Романович",
        "Проць Катерина Михайлівна",
    ],
    "АР-31": [
        "Середа Юлія Олександрівна",
        "Бойчук Іван Петрович",
        "Король Анастасія Сергіївна",
        "Пастернак Максим Андрійович",
    ],
}

TEACHERS = [
    "Іванюк Олег Олексійович",
    "Верес Зеновій Євгенович",
    "Лагун Ілона Ігорівна",
    "Стахів Роман Іванович",
    "Барановська Надія Михайлівна",
    "Банах Василь Михайлович",
    "Іваньо Святослав Михайлович",
    "Лильо Орест Миколайович",
    "Мельник Ростислав Ігорович",
    "Яцук Василь Олександрович",
    "Влах-Вигриновська Галина Іванівна",
    "Наконечний Адріан Йосифович",
    "Дзелендзяк Уляна Юріївна",
    "Соболевський Ігор Романович",
]

SUBJECTS = [
    ("Інтернет речей", 0, "exam"),
    ("Цифрова обробка сигналів", 1, "credit"),
    ("Бази даних", 2, "exam"),
    ("Комп'ютерні мережі", 3, "credit"),
    ("Проєктування програмного забезпечення", 4, "exam"),
    ("Алгоритми та структури даних", 5, "exam"),
    ("Програмування Python", 0, "exam"),
    ("Об'єктно-орієнтоване програмування", 4, "credit"),
    ("Архітектура комп'ютерів", 6, "exam"),
    ("Основи кібербезпеки", 7, "credit"),
    ("Метрологія", 8, "credit"),
    ("Економіка підприємства", 9, "exam"),
    ("Маркетинг", 10, "exam"),
    ("Основи менеджменту", 10, "credit"),
    ("Електротехніка", 11, "exam"),
    ("Транспортні системи", 12, "exam"),
    ("Інженерна графіка", 13, "credit"),
    ("Основи архітектурного проєктування", 13, "exam"),
]

GROUP_SUBJECTS = {
    "ІР-44": [
        "Інтернет речей", "Цифрова обробка сигналів",
        "Проєктування програмного забезпечення", "Бази даних",
    ],
    "ІР-34": [
        "Інтернет речей", "Комп'ютерні мережі",
        "Програмування Python", "Бази даних",
    ],
    "КН-31": [
        "Бази даних", "Комп'ютерні мережі",
        "Алгоритми та структури даних", "Об'єктно-орієнтоване програмування",
    ],
    "КН-21": [
        "Програмування Python", "Об'єктно-орієнтоване програмування",
        "Алгоритми та структури даних", "Бази даних",
    ],
    "ПЗ-21": [
        "Проєктування програмного забезпечення", "Об'єктно-орієнтоване програмування",
        "Програмування Python", "Бази даних",
    ],
    "КБ-41": [
        "Архітектура комп'ютерів", "Основи кібербезпеки",
        "Комп'ютерні мережі", "Алгоритми та структури даних",
    ],
    "КС-22": [
        "Архітектура комп'ютерів", "Метрологія",
        "Програмування Python", "Комп'ютерні мережі",
    ],
    "МЕ-31": [
        "Економіка підприємства", "Основи менеджменту", "Маркетинг",
    ],
    "МК-21": [
        "Маркетинг", "Основи менеджменту", "Економіка підприємства",
    ],
    "ЕЕ-21": [
        "Електротехніка", "Метрологія", "Програмування Python",
    ],
    "АТ-22": [
        "Транспортні системи", "Інженерна графіка", "Економіка підприємства",
    ],
    "АР-31": [
        "Основи архітектурного проєктування", "Інженерна графіка", "Економіка підприємства",
    ],
}

PAIRS = {
    1: (time(8, 30), time(9, 50)),
    2: (time(10, 5), time(11, 25)),
    3: (time(11, 40), time(13, 0)),
    4: (time(13, 15), time(14, 35)),
    5: (time(14, 50), time(16, 10)),
    6: (time(16, 25), time(17, 45)),
    7: (time(18, 0), time(19, 20)),
    8: (time(19, 30), time(20, 50)),
}


def check_demo_data():
    assert len(INSTITUTES) == 7
    assert len(GROUPS) == 12
    assert sum(len(names) for names in STUDENTS.values()) == 48
    assert len(set(name for names in STUDENTS.values() for name in names)) == 48
    subject_names = {name for name, _, _ in SUBJECTS}
    assert len(subject_names) == len(SUBJECTS)
    assert set(STUDENTS) == {name for name, _, _, _ in GROUPS}
    assert set(GROUP_SUBJECTS) == set(STUDENTS)
    for name, _, code, _ in GROUPS:
        assert code in INSTITUTES
        assert len(GROUP_SUBJECTS[name]) >= 3
        assert set(GROUP_SUBJECTS[name]) <= subject_names


def seed():
    check_demo_data()
    app = create_app()
    counts = Counter()
    warnings = []

    with app.app_context():
        db.create_all()
        institute_svc = InstituteService()
        specialty_svc = SpecialtyService()
        group_svc = AcademicGroupService()
        student_svc = StudentService()
        teacher_svc = TeacherService()
        subject_svc = SubjectService()
        schedule_svc = ScheduleService()
        grade_svc = GradeService()

        institutes = {}
        for code, name in INSTITUTES.items():
            institute = Institute.query.filter_by(name=name).first()
            if institute is None:
                institute = institute_svc.create(name)
                counts["Інститути"] += 1
            institutes[code] = institute

        specialties = {}
        groups = {}
        for group_name, course, institute_code, specialty_name in GROUPS:
            key = (institute_code, specialty_name)
            if key not in specialties:
                specialty = Specialty.query.filter_by(
                    name=specialty_name, institute_id=institutes[institute_code].id,
                ).first()
                if specialty is None:
                    specialty = specialty_svc.create(
                        specialty_name, institutes[institute_code].id
                    )
                    counts["Спеціальності"] += 1
                specialties[key] = specialty

            group = AcademicGroup.query.filter_by(name=group_name).first()
            if group is None:
                group = group_svc.create(
                    group_name, course, specialties[key].id
                )
                counts["Групи"] += 1
            elif group.course != course or group.specialty_id != specialties[key].id:
                warnings.append(
                    f"Група {group_name} вже існує з іншими параметрами; "
                    "її не змінено."
                )
            groups[group_name] = group

        students = {}
        for group_name, names in STUDENTS.items():
            group = groups[group_name]
            for full_name in names:
                student = Student.query.filter_by(full_name=full_name).first()
                if student is None:
                    student = student_svc.create(full_name, group.id)
                    counts["Студенти"] += 1
                elif student.group_id != group.id:
                    warnings.append(
                        f"{full_name} вже є в іншій групі; "
                        "залишено наявне призначення."
                    )
                students[full_name] = student

        teachers = []
        for full_name in TEACHERS:
            teacher = Teacher.query.filter_by(full_name=full_name).first()
            if teacher is None:
                teacher = teacher_svc.create(full_name)
                counts["Викладачі"] += 1
            teachers.append(teacher)

        subjects = {}
        assessment_types = {}
        for title, teacher_index, kind in SUBJECTS:
            subject = Subject.query.filter_by(name=title).first()
            if subject is None:
                subject = subject_svc.create(title, teachers[teacher_index].id)
                counts["Дисципліни"] += 1
            elif subject.teacher_id != teachers[teacher_index].id:
                warnings.append(
                    f"У дисципліни «{title}» уже інший викладач; "
                    "призначення збережено."
                )
            subjects[title] = subject
            assessment_types[title] = kind

        for group_name, subject_titles in GROUP_SUBJECTS.items():
            group = groups[group_name]
            for title in subject_titles:
                subject = subjects[title]
                if not any(item.id == subject.id for item in group.subjects):
                    group_svc.add_subject(group.id, subject.id)
                    counts["Призначення дисциплін"] += 1

        for group_index, (group_name, _, _, _) in enumerate(GROUPS):
            group = groups[group_name]
            for subject_index, title in enumerate(GROUP_SUBJECTS[group_name][:3]):
                subject = subjects[title]
                if ScheduleEntry.query.filter_by(
                    group_id=group.id, subject_id=subject.id
                ).first() is not None:
                    continue

                pair_count = len(PAIRS)

                preferred_day = (group_index + subject_index) % 5 + 1
                preferred_pair = (group_index + subject_index) % pair_count + 1

                classroom = f"{101 + group_index}"
                created = False

                for offset in range(5 * pair_count):
                    day = (preferred_day - 1 + offset // pair_count) % 5 + 1
                    pair = (preferred_pair - 1 + offset % pair_count) % pair_count + 1

                    start, end = PAIRS[pair]
                    try:
                        schedule_svc.create(
                            group.id, subject.id, day, start, end, classroom
                        )
                        counts["Заняття"] += 1
                        created = True
                        break
                    except ValueError:
                        continue
                if not created:
                    warnings.append(
                        f"Не вдалося підібрати вільний час: "
                        f"{group_name} — {title}."
                    )

        exam_scores = [93, 88, 74, 50, 51, 67, 96, 42, 81, 59, 77, 45]
        for group_index, (group_name, _, _, _) in enumerate(GROUPS):
            titles = GROUP_SUBJECTS[group_name]
            for student_index, full_name in enumerate(STUDENTS[group_name]):
                student = students[full_name]
                if student.group_id != groups[group_name].id:
                    continue
                for offset, title in enumerate(titles[:2]):
                    subject = subjects[title]
                    if Grade.query.filter_by(
                        student_id=student.id, subject_id=subject.id
                    ).first() is not None:
                        continue
                    kind = assessment_types[title]
                    try:
                        if kind == "exam":
                            score = exam_scores[
                                (group_index * 4 + student_index + offset) % len(exam_scores)
                            ]
                            grade_svc.add_exam(student.id, subject.id, score)
                        else:
                            passed = (group_index + student_index + offset) % 5 != 0
                            grade_svc.add_credit(student.id, subject.id, passed)
                        counts["Оцінки"] += 1
                    except (ValueError, LookupError) as exc:
                        warnings.append(
                            f"Не внесено результат {full_name} / {title}: {exc}"
                        )

        print("\nДемонстраційні дані оброблено (без видалення наявних записів).")
        print("План: 7 інститутів, 12 груп, 48 демонстраційних студентів.")
        print("Нові записи під час ЦЬОГО запуску:")
        for title in (
            "Інститути", "Спеціальності", "Групи", "Студенти", "Викладачі",
            "Дисципліни", "Призначення дисциплін", "Заняття", "Оцінки",
        ):
            print(f"  {title}: {counts[title]}")
        print("\nУсього в базі:")
        for title, model in (
            ("Інститути", Institute), ("Спеціальності", Specialty),
            ("Групи", AcademicGroup), ("Студенти", Student),
            ("Викладачі", Teacher), ("Дисципліни", Subject),
            ("Заняття", ScheduleEntry), ("Оцінки", Grade),
        ):
            print(f"  {title}: {db.session.query(model).count()}")
        if warnings:
            print("\nПопередження (наявні записи не змінено):")
            for warning in warnings:
                print("  -", warning)
        print("\nГотово. Дані можна переглянути в браузері.")


if __name__ == "__main__":
    seed()
