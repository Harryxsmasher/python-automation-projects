try:
    print("Start")
    raise ValueError("Invalid age")
    print("End")

except ValueError:
    print("Age error detected")