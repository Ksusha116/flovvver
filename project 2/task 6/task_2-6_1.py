pH = float(input("Введите значение pH: "))

if pH < 7:
    print("Кислая среда")
elif pH == 7:
    print("Нейтральная среда")
else:
    print("Щелочная среда")