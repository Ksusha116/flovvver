fio = input("ФИО исследователя: ")
data = input("Дата: ")
exp = input("Эксперимент: ")
ad = "-" * 50
with open("laba.txt", "w", encoding="utf-8") as file:
    file.write(f"+{ad}+\n| Электронный лабораторный журнал\t\t\t\t\t|\n+{ad}+\n|")