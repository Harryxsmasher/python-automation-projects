orderdb = []

class Order:
    def __init__(self, name, items, prices):
        self.name = name
        self.items = items
        self.prices = prices

    def display_order(self):
        print(self.name)

        item = self.items
        price = self.prices
        total = 0
        for i in range(len(self.items)):
            print(f"{item[i]} - {price[i]}")

            total += price[i] 
        print(f"total is {total}")


def add_order():
    name = input("Enter Customer name: ")
    number_of_items = int(input("Enter the number of items for the customer: "))
    items = []
    prices = []
    i = 1
    while i <= number_of_items:
        item = input("Enter the items for the customer: ")
        price = int(input("Enter the prices for the items: "))
        i += 1
        items.append(item)
        prices.append(price)
    order = Order(name, items, prices)
    orderdb.append(order)

def view_order():
    if not orderdb:
        print("No orders available")
        return
    for order in orderdb:
        order.display_order()

def search_order():
    name = input("Enter the search name for the order: ")
    found_status = False

    for order in orderdb:
        if order.name.lower() == name.lower():
            order.display_order()
            found_status = True
            break
    if not found_status:
        print("Customer not found")


while True:
    print("\nOrder Management System")
    print("1. Add Order")
    print("2. View Orders")
    print("3. Search Order")
    print("4. Exit")

    choice = input("Enter option: ")

    if choice == "1":
        add_order()
    elif choice == "2":
        view_order()
    elif choice == "3":
        search_order()
    elif choice == "4":
        print("Goodbye!")
        break
    else:
        print("Invalid option")