class Student:
    def __init__(self, name):
        self.name = name
        self.__marks = 0

    def set_marks(self, marks):

        if 0 <= marks <= 100:
            self.__marks = marks
            print("Marks updated Successfully")
        else:
            print("Invalid marks")
    
    def get_marks(self):
        return self.__marks
    

student = Student("Praveen")

student.set_marks(100)

print(student.get_marks())

