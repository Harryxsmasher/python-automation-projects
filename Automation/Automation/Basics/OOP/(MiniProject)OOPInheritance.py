# Inheritance Example
class Person:
    def __init__(self, Name, Age):
        self.Name = Name
        self.Age = Age



class Employee(Person):
    def __init__(self, Name, Age, EmployeeID, Salary):

        super().__init__(Name, Age)

        self.EmployeeID = EmployeeID
        self.Salary = Salary

class Manager(Employee):
    def __init__(self, Name, Age, EmployeeID, Salary, Department):

        super().__init__(Name, Age, EmployeeID, Salary)

        self.Department = Department

    def display_info(self):
        print(f"Employee InformationL\n ")
        print(f"Name: {self.Name}")
        print(f"Age: {self.Age}")
        print(f"EmployeeID: {self.EmployeeID}")
        print(f"Salary: {self.Salary}")
        print(f"Department: {self.Department}")



staff = Manager("Praveen", 30, "MM001", 60000, "IT")


staff.display_info()
