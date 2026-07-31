import numpy as np

temperatures = np.array([32, 30, 29, 31, 35, 36, 34])

first_temperature = temperatures[0]
last_temperature = temperatures[-1]
middle_three_temperature = temperatures[2:5]
total_number = len(temperatures)

print(first_temperature, last_temperature, middle_three_temperature, total_number)


