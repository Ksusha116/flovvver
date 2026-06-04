a = [int(input()) for i in range(int(input('Введите размер списка: ')))]
n = len(a)

i = 0
count = 0

while i<n:
    if a[i]>0:
        count += 1
    i += 1

print(count)