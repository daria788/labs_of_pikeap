import unittest
from rk2_refactored import (
    Lang, App, LangApp,
    create_one_to_many, create_many_to_many,
    task_b1, task_b2, task_b3
)

class TestRk2(unittest.TestCase):

    def setUp(self):
        """ Подготовка тестовых данных """
        self.apps = [
            App(1, "Visual Studio"),
            App(2, "PyCharm"),
            App(3, "Eclipse"),
            App(4, "VS Code"),
            App(5, "IntelliJ IDEA")
        ]
        self.langs = [
            Lang(1, "Python", 1991, 2),
            Lang(2, "Java", 1995, 3),
            Lang(3, "C#", 2000, 1),
            Lang(4, "JavaScript", 1995, 4),
            Lang(5, "Kotlin", 2011, 5),
            Lang(6, "TypeScript", 2012, 4),
            Lang(7, "Паскальов", 1970, 3)
        ]
        self.lang_apps = [
            LangApp(1, 2),
            LangApp(1, 4),
            LangApp(2, 3),
            LangApp(2, 5),
            LangApp(3, 1),
            LangApp(4, 4),
            LangApp(5, 5),
            LangApp(6, 4),
            LangApp(6, 2),
            LangApp(7, 5)
        ]

    def test_task_b1(self):
        """ Тест для задачи Б1: проверка сортировки по названию языка """
        one_to_many = create_one_to_many(self.langs, self.apps)
        result = task_b1(one_to_many)

        # Проверяем, что список отсортирован по названию языка (первый элемент кортежа)
        lang_names = [item[0] for item in result]
        self.assertEqual(lang_names, sorted(lang_names))

    def test_task_b2(self):
        """ Тест для задачи Б2: проверка подсчета языков в средах и сортировки по количеству """
        one_to_many = create_one_to_many(self.langs, self.apps)
        result = task_b2(self.apps, one_to_many)

        # Проверяем, что результат отсортирован по количеству (второй элемент кортежа)
        counts = [cnt for _, cnt in result]
        self.assertEqual(counts, sorted(counts))  # Должен быть отсортирован по возрастанию

        expected_counts = {
            "Visual Studio": 1,
            "PyCharm": 1,
            "Eclipse": 2,
            "VS Code": 2,
            "IntelliJ IDEA": 1
        }
        for app_name, count in result:
            self.assertEqual(count, expected_counts[app_name])

    def test_task_b3(self):
        """ Тест для задачи Б3: проверка фильтрации языков, заканчивающихся на 'ов' """
        many_to_many = create_many_to_many(self.langs, self.apps, self.lang_apps)
        result = task_b3(many_to_many)

        # Проверяем, что в результате есть только язык, заканчивающийся на 'ов'
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], "Паскальов")

        # Проверяем, что среда разработки для этого языка правильная
        self.assertEqual(result[0][1], "IntelliJ IDEA")

if __name__ == '__main__':
    unittest.main()