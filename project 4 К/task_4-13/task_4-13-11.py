a = [int(input()) for i in range(int(input('Введите размер списка: ')))]
n = len(a)

i = 0
sum = 0
count = 0

while i<n:
    if i % 2 == 0:
        sum += a[i]
        count += 1
    i += 1

print(sum/count)