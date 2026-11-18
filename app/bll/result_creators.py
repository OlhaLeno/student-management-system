
from abc import ABC, abstractmethod

from app.dal.models import Grade, ExamGrade, CreditGrade


class ResultCreator(ABC):

    @abstractmethod
    def create(
        self,
        student_id: int,
        subject_id: int,
        value: int | bool
    ) -> Grade:
        pass


class ExamCreator(ResultCreator):

    def create(
        self,
        student_id: int,
        subject_id: int,
        value: int | bool
    ) -> ExamGrade:

        if type(value) is not int:
            raise ValueError("Результат іспиту має бути числом.")

        return ExamGrade(
            student_id=student_id,
            subject_id=subject_id,
            score=value
        )


class CreditCreator(ResultCreator):

    def create(
        self,
        student_id: int,
        subject_id: int,
        value: int | bool
    ) -> CreditGrade:

        if type(value) is not bool:
            raise ValueError(
                "Результат заліку має бути True або False."
            )

        return CreditGrade(
            student_id=student_id,
            subject_id=subject_id,
            passed=value
        )
