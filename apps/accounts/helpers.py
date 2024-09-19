import typing

from apps.accounts.models import AccountType, UserAccount
from apps.students.models import Student


def get_student(email: str, matriculation_number: str) -> typing.Optional[Student]:
    """
    Returns student with the given email and matriculation number if it exists.

    :param email: Email of the student
    :param matriculation_number: Matriculation number of the student
    :return: Student object if it exists, else None
    """
    return Student.objects.filter(
        email__iexact=email, matriculation_number__iexact=matriculation_number
    ).first()


def create_account_for_student(
    student_email: str, student_name: str, password: str
) -> UserAccount:
    """
    Creates a new account for the student with the given email and password.

    :param student_email: Email of the student
    :param password: Password for the student
    """
    return UserAccount.objects.create_user(
        email=student_email,
        name=student_name,
        password=password,
        account_type=AccountType.STUDENT,
    )

        
