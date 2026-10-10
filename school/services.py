"""Бізнес-логіка: перевірки + збереження. Усі помилки — ValidationError."""
from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

from .models import Grade, Schedule, SchoolClass, Student, Subject, Teacher


def _save(obj):
    obj.full_clean()  # перевіряє унікальність, діапазони, clean()
    obj.save()
    return obj


def _get(model, label, **lookup):
    try:
        return model.objects.get(**lookup)
    except model.DoesNotExist:
        raise ValidationError(f"{label} не знайдено.")


# ---- Предмет ----
def add_subject(name, description=""):
    return _save(Subject(name=name.strip(), description=description.strip()))


def update_subject(name, new_name=None, new_description=None):
    s = _get(Subject, "Предмет", name=name)
    if new_name:
        s.name = new_name.strip()
    if new_description is not None:
        s.description = new_description.strip()
    return _save(s)


def delete_subject(name):
    s = _get(Subject, "Предмет", name=name)
    try:
        s.delete()
    except ProtectedError:
        raise ValidationError("Не можна видалити предмет, у якого є вчителі.")


# ---- Вчитель ----
def add_teacher(first_name, last_name, subject_name):
    subject = _get(Subject, "Предмет", name=subject_name.strip())
    return _save(Teacher(first_name=first_name.strip(), last_name=last_name.strip(), subject=subject))


# ---- Клас ----
def add_class(name, year):
    try:
        year = int(year)
    except (TypeError, ValueError):
        raise ValidationError("Рік навчання має бути числом.")
    return _save(SchoolClass(name=name.strip(), year=year))


def update_class(name, new_name=None, new_year=None):
    c = _get(SchoolClass, "Клас", name=name)
    if new_name:
        c.name = new_name.strip()
    if new_year:
        try:
            c.year = int(new_year)
        except ValueError:
            raise ValidationError("Рік навчання має бути числом.")
    return _save(c)


def delete_class(name):
    c = _get(SchoolClass, "Клас", name=name)
    try:
        c.delete()
    except ProtectedError:
        raise ValidationError("Не можна видалити клас, у якому є учні.")


# ---- Учень ----
def add_student(first_name, last_name, class_name):
    c = _get(SchoolClass, "Клас", name=class_name.strip())
    return _save(Student(first_name=first_name.strip(), last_name=last_name.strip(), school_class=c))


# ---- Розклад ----
def add_schedule(day_of_week, start_time, subject_name, class_name, teacher_first, teacher_last):
    try:
        day = int(day_of_week)
        t = datetime.strptime(start_time.strip(), "%H:%M").time()
    except ValueError:
        raise ValidationError("Невірний день (1-5) або час (формат ГГ:ХХ).")
    subject = _get(Subject, "Предмет", name=subject_name.strip())
    school_class = _get(SchoolClass, "Клас", name=class_name.strip())
    teacher = _get(Teacher, "Вчитель", first_name=teacher_first.strip(), last_name=teacher_last.strip())
    return _save(Schedule(day_of_week=day, start_time=t, subject=subject,
                          school_class=school_class, teacher=teacher))


# ---- Оцінка ----
def add_grade(first_name, last_name, subject_name, value, grade_date=None):
    student = _get(Student, "Учня", first_name=first_name.strip(), last_name=last_name.strip())
    subject = _get(Subject, "Предмет", name=subject_name.strip())
    try:
        value = int(value)
        d = datetime.strptime(grade_date.strip(), "%Y-%m-%d").date() if grade_date else date.today()
    except ValueError:
        raise ValidationError("Оцінка має бути числом, дата — у форматі РРРР-ММ-ДД.")
    return _save(Grade(student=student, subject=subject, value=value, date=d))
