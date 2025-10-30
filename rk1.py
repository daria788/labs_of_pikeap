from operator import itemgetter

class Lang:
    """Язык программирования"""
    def __init__(self, id, name, year, app_id):
        self.id = id
        self.name = name
        self.year = year
        self.app_id = app_id
class App:
    """Среда разработки"""
    def __init__(self, id, name):
        self.id = id
        self.name = name
class LangApp:
    """Реализация многие-ко-многим"""
    def __init__(self, lang_id, app_id):
        self.lang_id = lang_id
        self.app_id = app_id
apps=[
    App(1, "Visual Studio"),
    App(2, "PyCharm"),
    App(3, "Eclipse"),
    App(4, "VS Code"),
    App(5, "IntelliJ IDEA")
]
langs = [
    Lang(1, "Python", 1991, 2),
    Lang(2, "Java", 1995, 3),
    Lang(3, "C#", 2000, 1),
    Lang(4, "JavaScript", 1995, 4),
    Lang(5, "Kotlin", 2011, 5),
    Lang(6, "TypeScript", 2012, 4),
    Lang(7, "Паскальов", 1970, 3)  # добавлен для Б3
]
lang_apps = [
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
def main(): 
    one_to_many = [(l.name, l.year, a.name)
        for l in langs
        for a in apps
        if l.app_id == a.id
    ]
    many_to_many_temp = [(a.name, la.app_id, la.lang_id)
        for a in apps
        for la in lang_apps
        if a.id == la.app_id
    ]
    many_to_many = [(l.name, l.year, app_name)
        for app_name, app_id, lang_id in many_to_many_temp
        for l in langs if l.id == lang_id
    ]
    print('Task Б1')
    res_1=sorted(one_to_many,key=itemgetter(0))
    print(res_1)

    print('Task Б2')
    res_2_unsorted=[]
    for a in apps:
        lags_in_app=list(filter(lambda x: x[2]==a.name, one_to_many))
        count=len(lags_in_app)
        if count>0:
            res_2_unsorted.append((a.name, count))
    res_2 = sorted(res_2_unsorted,key=itemgetter(1))
    for app,cnt in res_2:
        print(f"Среда разработки:{app}, Кол-во языков: {cnt}")

    print("\nTask Б3")
    # Языки, название которых заканчивается на "ов"
    res_b3 = [
        (lang_name, app_name)
        for lang_name, year, app_name in many_to_many  # ← ИСПРАВЛЕНО: year вместо app_id
        if lang_name.endswith("ов")
    ]
    res_b3_unique = list(set(res_b3))
    if res_b3_unique:
        for lang, app in sorted(res_b3_unique):
            print(f"Язык: {lang}, Среда: {app}")
    else:
        print("Нет языков, название которых заканчивается на 'ов'.")

if __name__ == "__main__":
    main()
