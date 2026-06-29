
numbers = [12,5,20,8,30,15]


largest = 0
second_largest = 0

for num in numbers:
    if num > largest:
        second_largest = largest
        largest = num
    elif num > second_largest and num != largest:
        second_largest = num

print(largest)
print(second_largest)


