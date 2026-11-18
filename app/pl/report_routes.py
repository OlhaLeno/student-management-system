from app.bll.report_service import ReportService
from app.bll.report_strategies import GroupReport, TeacherReport, DebtReport
from app.pl.api_utils import make_api, query_int


report_api = make_api("report_api", __name__)


def generate_report(strategy, fields):
    filters = {}
    for field in fields:
        value = query_int(field)
        if value is not None:
            filters[field] = value
    service = ReportService()
    service.set_strategy(strategy)
    return service.generate(filters)


@report_api.get("/reports/groups")
def group_report():
    return generate_report(GroupReport(), ("group_id", "course"))


@report_api.get("/reports/teachers")
def teacher_report():
    return generate_report(TeacherReport(), ("teacher_id",))


@report_api.get("/reports/debts")
def debt_report():
    return generate_report(DebtReport(), ("group_id", "course", "student_id"))
