pitsreda = input("Введите название питательной среды: ")
agar = input("Введите концентрацию агара (%): ")
ster = input("Введите температуру стерилизации (°C): ")
with open("with recipe.txt", "w", encoding="utf-8") as card:
    card.write(f"{pitsreda}\n концентрация: {agar}\n температуры: {ster}")
print("Файл 'recipe.txt' успешно сформирован!")