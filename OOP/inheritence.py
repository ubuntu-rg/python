import csv


class Item:
    # Define a class level attribute
    pay_rate = 0.8
    # Save all instances in the 'all' array.
    all = []

    # Using the magic method __init__
    def __init__(self, name: str, price: float, quantity=0.0):
        # Run validation to the received arguments
        assert price >= 0, f"The price that was given ({price}) is not greater or equal to zero!"
        assert quantity >= 0, f"The quantity that was given ({quantity}) is not greater or equal to zero!"

        # Assign to self object
        self.name = name
        self.price = price
        self.quantity = quantity

        # Apply actions
        Item.all.append(self)

    def calculate_total_price(self):
        return self.price * self.quantity

    def apply_discount(self):
        self.price = self.price * self.pay_rate

    # Change instance method to a class method using decorator:
    @classmethod
    def instantiate_from_csv(cls):
        with open("items.csv", "r") as file:
            reader = csv.DictReader(file)
            items = list(reader)
        for item in items:
            Item(
                name=item.get('name'),
                price=float(item.get('price')),
                quantity=float(item.get('quantity'))
            )

    @staticmethod
    def is_integer(num):
        if isinstance(num, float):
            # is_integer will return true if the number is rounded, i.e 7.0, 5.0
            return num.is_integer()
        return True

    # Return the name of the object, so it can be read. Using represents.
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}', {self.price}, {self.quantity})"


class Phone(Item):
    def __init__(self, name: str, price: float, quantity=0.0, broken_phones=0):
        # Initiate the values from the parent class.
        super().__init__(
            name, price, quantity
        )
        # Run validation to the received arguments
        assert quantity >= 0, f"The Broken Phones that was given ({broken_phones}) is not greater or equal to zero!"

        # Assign to self object
        self.broken_phones = broken_phones


phone1 = Phone("Galaxy V12", 3499, 5, 1)
print(Item.all)
print(Phone.all)
