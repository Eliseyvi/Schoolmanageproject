from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Subject(models.Model):
    name = models.CharField("Назва", max_length=100, unique=True)
    description = models.TextField("Опис", blank=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    first_name = models.CharField("Ім'я", max_length=50)
    last_name = models.CharField("Прізвище", max_length=50)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="teachers")

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.subject})"


class SchoolClass(models.Model):  # "Class" — зарезервоване слово Python
    name = models.CharField("Назва", max_length=20, unique=True)
    year = models.PositiveSmallIntegerField(
        "Рік навчання", validators=[MinValueValidator(1), MaxValueValidator(11)]
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    first_name = models.CharField("Ім'я", max_length=50)
    last_name = models.CharField("Прізвище", max_length=50)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name="students")

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.school_class})"


class Schedule(models.Model):
    DAYS = [(1, "Понеділок"), (2, "Вівторок"), (3, "Середа"), (4, "Четвер"), (5, "П'ятниця")]

    day_of_week = models.PositiveSmallIntegerField("День тижня", choices=DAYS)
    start_time = models.TimeField("Початок")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = [("day_of_week", "start_time", "school_class")]
        ordering = ["day_of_week", "start_time"]

    def clean(self):
        if self.teacher_id and self.subject_id and self.teacher.subject_id != self.subject_id:
            raise ValidationError("Цей вчитель не викладає обраний предмет.")

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time:%H:%M} — {self.school_class}, {self.subject}"


class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grades")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(
        "Оцінка", validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    date = models.DateField("Дата")

    def __str__(self):
        return f"{self.student}: {self.subject} = {self.value} ({self.date})"
