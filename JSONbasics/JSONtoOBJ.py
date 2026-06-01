import json
student_object = []
with open("student.json", "r") as f:
    student_dict = json.load(f)


class Student:
    def __init__(self, name, mark):
        self.name = name
        self.mark = mark

    def print_info(self):
        print(f"Name: {self.name} | Mark: {self.mark}")


def test_loop():
    for student in student_dict:
        student = Student(student["name"], student["mark"])
        student_object.append(student)


def print_student():
    for student in student_object:
        student.print_info()

test_loop()
print_student()


