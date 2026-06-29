from pathlib import Path
import json

file_path = Path(r"C:\Users\50008944\pythonrefresh\Automation\Automation")
file_name = "employee.json"

full_path = file_path / file_name
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

with open(full_path, "w") as f:
    json.dump(employees, f, indent=4)
print("Data saved.")


with open(full_path, "r") as f:
    p_obj = json.load(f)

print("Data loaded from JSON file!")

for emp_data in p_obj:
    print(f"{emp_data["Name"]} - {emp_data["Department"]} - {emp_data["Experience"]}")


