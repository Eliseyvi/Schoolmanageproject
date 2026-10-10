from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from . import services as s


class ServicesTests(TestCase):
    def setUp(self):
        self.math = s.add_subject("Математика", "Алгебра")
        self.teacher = s.add_teacher("Ірина", "Коваль", "Математика")
        self.cls = s.add_class("5-А", 5)
        self.student = s.add_student("Олег", "Бондар", "5-А")

    def test_subject_unique(self):
        with self.assertRaises(ValidationError):
            s.add_subject("Математика")

    def test_teacher_requires_subject(self):
        with self.assertRaises(ValidationError):
            s.add_teacher("А", "Б", "Фізика")

    def test_class_unique_and_year_range(self):
        with self.assertRaises(ValidationError):
            s.add_class("5-А", 5)
        with self.assertRaises(ValidationError):
            s.add_class("12-А", 12)

    def test_student_requires_class(self):
        with self.assertRaises(ValidationError):
            s.add_student("А", "Б", "9-Я")

    def test_schedule_ok_and_conflicts(self):
        s.add_schedule("1", "08:30", "Математика", "5-А", "Ірина", "Коваль")
        with self.assertRaises(ValidationError):  # той самий слот у класу
            s.add_schedule("1", "08:30", "Математика", "5-А", "Ірина", "Коваль")
        with self.assertRaises(ValidationError):  # невірний час
            s.add_schedule("1", "99:99", "Математика", "5-А", "Ірина", "Коваль")

    def test_schedule_teacher_must_teach_subject(self):
        s.add_subject("Історія")
        with self.assertRaises(ValidationError):
            s.add_schedule("2", "09:30", "Історія", "5-А", "Ірина", "Коваль")

    def test_grade(self):
        g = s.add_grade("Олег", "Бондар", "Математика", "10", "2026-10-01")
        self.assertEqual(g.date, date(2026, 10, 1))
        with self.assertRaises(ValidationError):
            s.add_grade("Олег", "Бондар", "Математика", "13")

    def test_delete_protected(self):
        with self.assertRaises(ValidationError):
            s.delete_subject("Математика")
        with self.assertRaises(ValidationError):
            s.delete_class("5-А")

    def test_update_subject(self):
        s.update_subject("Математика", "Алгебра і геометрія")
        self.assertTrue(s.Subject.objects.filter(name="Алгебра і геометрія").exists())
