
my_expenses = []
while True:
    print("1. Add Expenses")
    print("2. View Expenses")
    print("3. Sum Expenses")
    print("4. Search Expenses")
    print("5. Delete Expenses")
    print("6. Exit")
    print("---------------------------------")
    menu_option = input("Enter the option: ")
    if menu_option == "1":
        print("Add Expenses")
        title = input("Enter the expense task: ")
        amount = float(input("Enter the expense amount: "))

        expense = {"title" : title, "amount": amount}
        my_expenses.append(expense)
        print("Expenses Added Successfully")
        continue
    elif menu_option == "2":
        print("View Expenses")
        for expense in my_expenses:
            print(expense)
        continue
    elif menu_option == "3":
        print("Sum Expenses")
        total = 0
        for expense in my_expenses:
            total = total + expense["amount"]
            
        print(f"{total} are the total expense made")
        continue
    elif menu_option == "4":
        print("Search Expenses")
        search_expense = input("Enter to search an Expense: ")
        found_status = False
        for expense in my_expenses:
            if search_expense == expense["title"]:
                found_status = True
                print(f"{expense} has been found!")
                break
        if not found_status:
            print(f"{expense} not found!")
        continue
    elif menu_option == "5":
        print("Delete Expenses")
        search_expense = input("Enter to search an Expense: ")
        found_status = False
        for expense in my_expenses:
            if search_expense == expense["title"]:
                found_status = True
                my_expenses.remove(expense)
                print(f"{expense} has been Deleted!")
                break
        if not found_status:
            print(f"{expense} not found!")
        continue
    elif menu_option == "6":
        print("Good bye!")
        exit()