weight = float(input("Введите вес (кг): "))
height = float(input("Введите рост (см): "))
bmi = weight / (height ** 2)
print(f"--- Отчет о состоянии здоровья ---\n Рост: {height}\n Вес: {weight}\n Индекс массы тела: {bmi:.2f}")