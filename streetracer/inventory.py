class InventoryModule:
    def __init__(self, starting_cash=5000):
        self.cash_balance = starting_cash
        self.cars = {}      # format: {car_id: {"model": "Nissan Skyline R34", "condition": 100}}
        self.parts = {}     # format: {"Turbocharger": 2, "Racing Slicks": 8}
        self.tools = set()  # using a set because you either have a tool or you don't (no duplicates)
        self.car_id_counter = 1

    def update_cash(self, amount):
        """Adds or subtracts cash. Returns False if transaction would result in negative balance."""
        if self.cash_balance + amount < 0:
            print(f"TRANSACTION FAILED: Insufficient funds. Balance: ${self.cash_balance}, Attempted: ${amount}")
            return False
        
        self.cash_balance += amount
        action = "Earned" if amount > 0 else "Spent"
        print(f"CASH UPDATE: {action} ${abs(amount)}. New Balance: ${self.cash_balance}")
        return True

    def add_car(self, model_name):
        """Purchases/adds a car to the garage."""
        car_id = f"CAR-{self.car_id_counter:03d}"
        self.cars[car_id] = {
            "model": model_name,
            "condition": 100  # starts in perfect condition
        }
        self.car_id_counter += 1
        print(f"GARAGE: Added {model_name} (ID: {car_id})")
        return car_id

    def update_car_condition(self, car_id, damage_amount):
        """Applies damage to a car. Useful for Race and Mission modules."""
        if car_id not in self.cars:
            print(f"ERROR: Car {car_id} not found in garage.")
            return False
        
        current_condition = self.cars[car_id]["condition"]
        new_condition = max(0, current_condition - damage_amount)
        self.cars[car_id]["condition"] = new_condition
        
        print(f"GARAGE: {self.cars[car_id]['model']} condition is now {new_condition}%")
        return True

    def get_all_cars(self):
        """Returns all the cars owned"""
        return self.cars

    def get_available_cars(self):
        """Returns cars that are in good enough condition to race (>20%)."""
        return {cid: data for cid, data in self.cars.items() if data["condition"] > 20}

    def add_part(self, part_name, quantity):
        if part_name in self.parts:
            self.parts[part_name] += quantity
        else:
            self.parts[part_name] = quantity
        print(f"INVENTORY: Added {quantity}x {part_name}. Total: {self.parts[part_name]}")

    def use_part(self, part_name, quantity):
        """Consumes a part. Fails if not enough parts are available."""
        if self.parts.get(part_name, 0) >= quantity:
            self.parts[part_name] -= quantity
            print(f"INVENTORY: Used {quantity}x {part_name}. Remaining: {self.parts[part_name]}")
            return True
        print(f"ERROR: Not enough {part_name} in inventory.")
        return False

    def add_tool(self, tool_name):
        self.tools.add(tool_name)
        print(f"INVENTORY: Acquired tool: {tool_name}")
        
    def get_inventory_report(self):
        return {
            "Cash": self.cash_balance,
            "Cars": self.cars,
            "Parts": self.parts,
            "Tools": list(self.tools)
        }