class Person:
    def __init__(self, Name, Age):
        self.Name = Name
        self.Age = Age
    

class Employee(Person):
    def __init__(self, Name, Age, EmployeeID, Department, Salary):

        super.__init__(Name, Age)
        self.EmployeeID = EmployeeID
        self.Department = Department
        self.__Salary = 0

    def set_salary(self, Salary):

        if 0 <= Salary:
            self.__Salary = Salary
            print("Salary updated")
        else:
            print("Invalid Salary")
    
    def get_salary(self):
        return self.__Salary
    
    def view_employee(self):
        print("------------------------------------")
        print("Employee Information")
        print(f"Name: {self.Name}")
        print(f"Age: {self.Age}")
        print(f"Employee ID: {self.EmployeeID}")
        print(f"Department: {self.Department}")
        print(f"Salary: {self.__Salary}")
    


    

while True:
    print("Employee Management System")
    print("1. Add Employee")
    print("2. View Employee")
    print("3. Search Employee")
    print("4. Remoive Employee")
    print("5. Update Salary")
    print("6. Generate Report")
    print("7. Save")
    print("8. Load")
    print("9. Exit")









        