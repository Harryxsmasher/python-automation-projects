employeedb = []

class Employee:
    def __init__(self, name, salary, department):
        self.name = name
        self.salary = salary
        self.department = department
    
    def display_employee(self):
        print(f"Name of the employee: {self.name}")
        print(f"Salary of the employee: {self.salary}")
        print(f"Department of the employee: {self.department}")
    
    def increase_salary(self, percent):
        self.salary += (self.salary * percent / 100)
        
    

def add_employee():
    print("Add Employee!")
    name = input("Enter the Employee name: ")
    salary = int(input("Enter the Employee salary: "))
    department = input("Enter the Employee department: ")

    employee = Employee(name, salary, department)
    employeedb.append(employee)

def view_employee():
    if not employeedb:
        print("Employee not found!")
    for employee in employeedb:
        employee.display_employee()


def increase_salary():
    emp_name = input("Enter the employee name: ")
    percent = float(input("Enter the percentage: "))
    found_status = False
    for employee in employeedb:
        if emp_name.lower() == employee.name.lower():
            found_status = True
            employee.increase_salary(percent)
            employee.display_employee()
            break
    if not found_status:
        print("Employee not found!")




def search_employee():
    search_input = input("Enter the employee name to find: ")
    found_status = False
    for employee in employeedb:
        if search_input.lower() == employee.name.lower():
            found_status = True
            employee.display_employee()
            break
    if not found_status:
        print("Employee not found!")


while True:
    print("Employee Management System!")
    print("1. Add Employee")
    print("2. View Employee")
    print("3. Search Employee")
    print("4. Increase Salary")
    print("5. Exit")
    menu = input("Enter your option: ")
    if menu == "1":
        add_employee()
        continue
    elif menu == "2":
        view_employee()
        continue
    elif menu == "3":
        search_employee()
        continue
    elif menu == "4":
        increase_salary()
        continue
    elif menu == "5":
        print("Good bye!")
        break
