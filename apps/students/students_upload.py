import csv
import io
import re
import typing
from django.core.files import File
from django.db import models

from .models import Student, AcademicLevel

EXPECTED_DETAIL_COLUMNS = (
    "name",
    "email",
    "matriculation_number",
    "level",
)


def _clean_field_name(name: str) -> str:
    # Strip leading/trailing spaces and replace spaces with underscores
    name = name.strip().lower().replace(" ", "_")

    # Use regex to remove everything after '(', '/', or any other symbol
    name = re.sub(r"[\(/].*", "", name)

    # Strip trailing underscores (in case there was a space before the symbol)
    return name.rstrip("_")


def import_students_from_file(students_file: File) -> typing.List[Student]:
    """
    Import student details from a CSV file.

    Use details to create students
    """
    string_io = io.StringIO(students_file.read().decode("utf-8"))
    reader = csv.DictReader(string_io, skipinitialspace=True)
    reader.fieldnames = [_clean_field_name(field) for field in reader.fieldnames]
    print(reader.fieldnames)

    # Ensure all expected columns are present in the DataFrame
    missing_columns = set(EXPECTED_DETAIL_COLUMNS) - set(reader.fieldnames)
    if missing_columns:
        raise ValueError(
            f"Missing columns in student details file: {', '.join(missing_columns)}"
        )

    new_students = []
    for row in reader:
        data = {col: row[col] for col in EXPECTED_DETAIL_COLUMNS}

        name: str = data["name"]
        email: str = data["email"]
        matriculation_number: str = data["matriculation_number"]
        level: str = data["level"]
        # Remove all non-numeric characters from the level
        level = re.sub(r"\D", "", level)
        department: typing.Optional[str] = data.get("department", None)

        student_data = {
            "name": name.strip().title(),
            "email": email.strip().lower(),
            "matriculation_number": matriculation_number.strip()
            .upper()
            .replace("\\", "/"),
            "level": AcademicLevel(str(level).strip()),
        }
        if department:
            student_data["department"] = department.strip().title()

        # Skip students whose email or matriculation number already exists
        if Student.objects.filter(
            models.Q(email=email) | models.Q(matriculation_number=matriculation_number)
        ).exists():
            continue
        
        student = Student(**student_data)
        new_students.append(student)

    return Student.objects.bulk_create(new_students, batch_size=998)
