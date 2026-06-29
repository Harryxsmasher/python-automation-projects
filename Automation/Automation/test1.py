from pathlib import Path
import json

employees = []
file_path = Path(r"C:\Users\50008944\pythonrefresh\Automation\Automation")
file_name = "employee.json"

full_path = file_path / file_name


def add_emp(name, department, experience):
    emp_data = {"Name": name, "Department": department, "Experience": experience}
    employees.append(emp_data)

def dump_data(employees):
    with open(full_path, "w") as f:
        json.dump(employees, f, indent=4)
    print("Data Saved Successfully")

def search_employee(search_name, employees):
    found_status = False
    for emp in employees:
        if search_name == emp["Name"]:
            found_status = True
            print(f"Name: {emp["Name"]} - Department: {emp["Department"]} - Experience: {emp["Experience"]} years")
            break
    if not found_status:
        print("Employee not found!")

def load_data():
    with open(full_path, "r") as f:
        employee_data = json.load(f)

    for emp in employee_data:
        print(f"Name: {emp["Name"]} - Department: {emp["Department"]} - Experience: {emp["Experience"]} years")

while True:
    print("Employee Management System!(With JSON)")
    print("1. Add Employee")
    print("2. View Employee")
    print("3. Search employee")
    print("4. Exit")


    user_input = input("enter your option: ")
    if user_input == "1":
        name = input("Enter the employee name: ")
        department = input("Enter the employee department: ")
        experience = input("Enter the employee experience: ")
        add_emp(name, department, experience)
        dump_data(employees)
    elif user_input == "2":
        load_data()
    elif user_input == "3":
        search_name = input("Enter the name to search: ")
        search_employee(search_name, employees)
    elif user_input == "4":
        print("Good bye!")
        break


        


