order_db = []


def add_order(order_db):
        print("Add an order!")
        item = []
        price = []
        customer_name = input("Enter the name of the customer: ")
        no_of_items = int(input("Enter the number of items: "))
        i = 1
        while i <= no_of_items:
            
            item_name = input("Enter the name of the item: ")
            item_price = int(input("Enter the price of the item: "))
            item.append(item_name)
            price.append(item_price)
            i += 1
        orders = {"customer_name" : customer_name, "items" : item, "prices" : price}
        order_db.append(orders)
        print("Orders are added successfully")



while True:
    print("Welcome to Order Management System")
    print("Choose from the menu")
    print("1. Add order")
    print("2. View order")
    print("3. Search order")
    print("4. Total bill")
    print("5. Exit")
    menu = input("Enter: ")
    
    if menu == "1":
        add_order(order_db)
        continue
    elif menu == "2":
        print("View order")    
        continue
    elif menu == "3":
        print("Search order")
        continue
    elif menu == "4":
        print("Total bill")
        continue
    elif menu == "5":
            exit()