#class
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def display_info(self):
        print(f"name: {self.name}, marks: {self.marks}")
        return

#object
student = Student("Praveen", 100)

print(student.display_info())
