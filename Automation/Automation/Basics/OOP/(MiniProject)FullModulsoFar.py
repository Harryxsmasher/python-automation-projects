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




        