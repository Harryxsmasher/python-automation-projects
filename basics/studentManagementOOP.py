studentdb = []
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    
    def display_students(self):
        print(self.name)

        mark = self.marks
        