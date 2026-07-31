class Student:
    def __init__(self, name, subject):
        # Public Variable (It can be accessed from anywhere by any program)
        self.name = name
        # Encapsulated an attribute as a Protected (Protected Members (_): Prefixed with a single underscore. This is a convention warning other developers that the member is intended for internal use or subclasses. Python will not prevent external access)
        self._subject = subject
        # Encapsulated an attribute as a private (: Prefixed with a double underscore. This triggers Name Mangling, where Python internally renames the variable to _ClassName__variable)
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

