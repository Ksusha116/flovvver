baza = input("Введите имя оператора: ")
davlenie = input("Введите текущее значение давления (Па): ")
with open("sensor_log.txt", "w", encoding="utf-8") as file:
    file.write(f"ОПЕРАТОР:\t{baza}\n")
    file.write(f"ЗНАЧЕНИЕ:\t{davlenie}\n")
    print("Данные успешно сохранены в sensor_log.txt")