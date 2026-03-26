V = int(input("нужный объем раствора (в мл): "))
solb = round(V * 0.009, 2)
voda = round(V + solb, 2)
kal = "-" * 23
with open("recipe2.txt", "w", encoding="utf-8") as file:
    file.write("ОТЧЕТ ПО ПРИГОТОВЛЕНИЮ:\n")
    file.write(f"{kal}\n")
    file.write(f"Общий объем: {voda} мл\nМасса соли: {solb} г\nОбъем воды: {voda} мл")