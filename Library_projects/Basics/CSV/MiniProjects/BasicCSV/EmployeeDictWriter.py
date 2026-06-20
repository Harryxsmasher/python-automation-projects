from pathlib import Path
import csv

employees = [
    {
        "Name": "Praveen",
        "Department": "XR",
        "Experience": 2
    },
    {
        "Name": "John",
        "Department": "IT",
        "Experience": 5
    },
    {
        "Name": "Mary",
        "Department": "HR",
        "Experience": 3
    }
]

headers = ["Name", "Department", "Experience"]

csv_file = Path(
    r"C:\Users\Prave\Desktop\Projects\python-automation-projects\Library_projects\Basics\CSV\MiniProjects\BasicCSV"
) / "employee.csv"

with open(csv_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=headers)

    writer.writeheader()
    writer.writerows(employees)

print("Dictionary file loaded")
