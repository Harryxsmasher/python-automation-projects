#expected output
'''
=========================
Student Performance Report
=========================

Marks: [85 92 78 95 88]

Highest Mark : 95

Lowest Mark : 78

Total Marks : 438

Average Mark : 87.6

Highest Mark Position : 3

Lowest Mark Position : 2

'''

import numpy as np

marks = np.array([85, 92, 78, 95, 88])
print("Marks Report")
print(f"Highest Mark : {np.max(marks)}")
print(f"Lowest Mark : {np.min(marks)}")
print(f"Total Marks : {np.sum(marks)}")
print(f"Average Mark : {np.mean(marks)}")
print(f"Highest Mark Position : {np.argmax(marks)}")
print(f"Lowest Mark Position : {np.argmin(marks)}")

print("\n")
attendance = np.array([92, 88, 96, 81, 90])
print("Attendance Report")
print(f"Highest Mark : {np.max(attendance)}")
print(f"Lowest Mark : {np.min(attendance)}")
print(f"Total Marks : {np.sum(attendance)}")
print(f"Average Mark : {np.mean(attendance)}")
print(f"Highest Mark Position : {np.argmax(attendance)}")
print(f"Lowest Mark Position : {np.argmin(attendance)}")

