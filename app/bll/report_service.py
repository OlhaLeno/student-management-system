
from app.bll.grade_service import GradeService
from app.bll.report_strategies import ReportStrategy, GroupReport


class ReportService:

    def __init__(self):
        self._grades = GradeService()
        self._strategy = GroupReport()

    def set_strategy(self, strategy: ReportStrategy) -> None:
        self._strategy = strategy

    def generate(self, filters: dict) -> dict:
        grades = self._grades.all_grades()

        return self._strategy.generate(grades, filters)
