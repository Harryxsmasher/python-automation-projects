from pathlib import Path
import csv

employees = [
    ["Praveen", "XR", 2],
    ["John", "IT", 5],
    ["Mary", "HR", 3]
]

headers = ["Name","Department","Experience"]

csv_file = Path(
    r"C:\Users\Prave\Desktop\Projects\python-automation-projects\Library_projects\Basics\CSV\MiniProjects\BasicCSV"
) / "employee.csv"

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow(headers)
    writer.writerows(employees)

print("CSV File successfully Created")




