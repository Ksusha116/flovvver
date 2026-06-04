list = [int(input()) for i in range(int(input('Введите размер списка: ')))]
sum = 0
i = 0
size = len(list)-1

while i<=size:
    sum += (list[i])**2
    i+=1

print(sum)