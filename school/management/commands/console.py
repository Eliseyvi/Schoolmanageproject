from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand

from school import services as s

MENU = """
=== Шкільний розклад ===
1. Додати предмет          6. Додати оцінку
2. Додати вчителя          7. Редагувати предмет
3. Додати клас             8. Видалити предмет
4. Додати учня             9. Редагувати клас
5. Додати заняття в розклад 10. Видалити клас
0. Вихід
"""


def ask(prompt):
    return input(f"{prompt}: ").strip()


class Command(BaseCommand):
    help = "Консольний інтерфейс керування шкільним розкладом"

    def handle(self, *args, **options):
        actions = {
            "1": lambda: s.add_subject(ask("Назва"), ask("Опис")),
            "2": lambda: s.add_teacher(ask("Ім'я"), ask("Прізвище"), ask("Предмет")),
            "3": lambda: s.add_class(ask("Назва (напр. 5-А)"), ask("Рік навчання (1-11)")),
            "4": lambda: s.add_student(ask("Ім'я"), ask("Прізвище"), ask("Клас")),
            "5": lambda: s.add_schedule(ask("День тижня (1-5)"), ask("Початок (ГГ:ХХ)"), ask("Предмет"),
                                        ask("Клас"), ask("Ім'я вчителя"), ask("Прізвище вчителя")),
            "6": lambda: s.add_grade(ask("Ім'я учня"), ask("Прізвище учня"), ask("Предмет"),
                                     ask("Оцінка (1-12)"), ask("Дата РРРР-ММ-ДД (Enter = сьогодні)")),
            "7": lambda: s.update_subject(ask("Поточна назва"), ask("Нова назва (Enter = без змін)"),
                                          ask("Новий опис (Enter = без змін)") or None),
            "8": lambda: s.delete_subject(ask("Назва")),
            "9": lambda: s.update_class(ask("Поточна назва"), ask("Нова назва (Enter = без змін)"),
                                        ask("Новий рік (Enter = без змін)")),
            "10": lambda: s.delete_class(ask("Назва")),
        }
        while True:
            print(MENU)
            choice = ask("Ваш вибір")
            if choice == "0":
                break
            action = actions.get(choice)
            if not action:
                print("Невірний пункт меню.")
                continue
            try:
                result = action()
                print(f"OK: {result if result else 'виконано'}")
            except ValidationError as e:
                print("Помилка:", "; ".join(e.messages))
