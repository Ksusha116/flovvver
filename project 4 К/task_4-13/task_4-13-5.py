list = [int(input()) for i in range(int(input('Введите размер списка: ')))]
max = list[0]
i = 1
size = len(list)-1

while i<=size:
    if max < list[i]:
        max = list[i]
    i += 1

print(max)