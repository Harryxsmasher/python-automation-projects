try:
    first_number = int(input("Enter the first number: "))
    second_number = int(input("Enter the second number: "))
    result = first_number / second_number

except ZeroDivisionError:
    print("The value cannot be divided by 0")

except ValueError:
    print("Enter a valid number")

else:
    print(result)

finally:
    print("Program finished")