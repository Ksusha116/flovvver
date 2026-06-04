a = [int(input()) for i in range(int(input('Введите размер списка: ')))]
n = len(a)

i = 0
sum = 0

while i<n:
    sum += a[i]
    i += 1

print(sum/n)