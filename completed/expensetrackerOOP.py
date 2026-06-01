expenses = []

class Expense:
    def __init__(self, title, amount, category):
        self.title = title
        self.amount = amount
        self.category = category

    def displayExpenses(self):
        print(f"Title: {self.title}")
        print(f"Amount: {self.amount}")
        print(f"Category: {self.category}")
    
   
    


def add_expense():
    title = input("Enter the title of the expenses: ")
    amount = int(input("Enter the amount of the expenses: "))
    category = input("Enter the category for the expense entitled to: ")

    expense = Expense(title, amount, category)
    expenses.append(expense)

def view_expense():
    if not expenses:
        print("No data is available!")

    for expense in expenses:
        expense.displayExpenses()

def total_expense():
    total = 0
    for expense in expenses:
        # print(expense.amount)
        total += expense.amount
    print(f"Total Amount: {total}")

def total_expense_by_category():
    category = input("Enter the category you want to total: ")
    foundStatus = False
    totalForCategory = 0
    for expense in expenses:
        if category.lower() == expense.category.lower():
            foundStatus = True
            print(expense.amount)
            totalForCategory += expense.amount
    print(f"Category is: {expense.category} and total is: {totalForCategory}")
    if not foundStatus:
        print("Category not found")


while True:
    print("Expense Tracker!")
    print("1. Add Expense")
    print("2. View Expense")
    print("3. Total Expense")
    print("4. Total Expense by Category")
    print("5. Exit")

    menu = input("Enter the option: ")
    if menu == "1":
        add_expense()
        continue
    elif menu == "2":
        view_expense()
        continue
    elif menu == "3":
        total_expense()
        continue
    elif menu == "4":
        total_expense_by_category()
        continue
    elif menu == "5":
        print("Good bye!")
        break