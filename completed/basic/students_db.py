students_db = []

def add_students(students_db):
    marks_list = []
    students_name = input("Enter the student name: ")
    subjects = int(input("Enter how many subjects of marks needs to be entered: "))
    i = 1
    while i <= subjects:
        marks = int(input("Enter the marks: "))
        marks_list.append(marks)
        i += 1
    print("Marks added successfully")
    students = {"Name" : students_name, "marks" : marks_list}
    students_db.append(students)
    print("Student information Added Successfully")

                
def view_students(students_db):
    for student in students_db:
        printStudentDetails(student)

def search_students(students_db):
    search_Stu = input("Enter the student name: ")
    found_status = False

    for student in students_db:
        if search_Stu == student["Name"]:
            found_status = True
            printStudentDetails(student)
            break

    if not found_status:
        print("Student not found")
     
     

def printStudentDetails(student):
    print(student["Name"])
    total = 0
    for mark in student["marks"]:
        print(f"Marks: {mark}")
        total += mark

    print(f"Total Marks: {total}")
    average = total / len(student["marks"])
    print(f"Average of the student: {average}")
    status = None
    if average >= 40:
        status = "Pass"
    else:
        status = "Fail"
    print(f"Status: {status}")



def topper(students_db):
        max_average = 0
        top_student = None
        for students in students_db:
            total = 0
            for Marks in students["marks"]:
                total = Marks + total
            listofsubjects = len(students["marks"])
            average = total / listofsubjects
            if average > max_average:
                max_average = average
                top_student = students["Name"]
        print(f"Top Scorer: {top_student} with average {max_average}")

while True:
    print("Students Database!")
    print("1. Add Students!")
    print("2. View Students!")
    print("3. Search Students!")
    print("4. Top Scorer")
    print("5. Exit")

    menu = input("Enter menu option: ")
    if menu == "1":
        add_students(students_db)
        continue
    elif menu == "2":
        view_students(students_db)
        continue
    elif menu == "3":
        search_students(students_db)
        continue
    elif menu == "4":
        topper(students_db)
        continue
    elif menu == "5":
        print("Good bye")
        exit()