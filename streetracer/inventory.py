"""
Inventory Module
-----------------
Tracks the team's cash balance, garage (cars), spare parts,
and tools.  Acts as the financial ledger for the whole system.
"""

class InventoryModule:
    def __init__(self, starting_cash: int = 5000):
        self.cash_balance: int = starting_cash
        # {car_id: {"model": str, "condition": int, "assigned_to_race": bool}}
        self.cars:  dict = {}
        # {"Turbocharger": 2, ...}
        self.parts: dict = {}
        # set of tool name strings
        self.tools: set = set()
        self.car_id_counter: int = 1
        # simple transaction log
        self.transaction_log: list = []

    def update_cash(self, amount: int, reason: str = "") -> bool:
        """
        Adds or subtracts cash. 
        Returns False if transaction would result in negative balance.
        """
        if self.cash_balance + amount < 0:
            print(f"FAIL [Inventory]: Insufficient funds. "
                  f"Balance: ${self.cash_balance}, Attempted change: ${amount}")
            return False
        
        self.cash_balance += amount
        self.transaction_log.append({"amount": amount, "reason": reason,
                                     "balance_after": self.cash_balance})
        action = "Earned" if amount >= 0 else "Spent"
        label = f" ({reason})" if reason else ""
        print(f"CASH [{action}]: ${abs(amount)}{label}. "
              f"New Balance: ${self.cash_balance}")
        return True

    def add_car(self, model_name: str) -> str:
        """Adds a new car to the garage at 100% condition."""
        if not model_name or not model_name.strip():
            print("FAIL [Inventory]: Car model name cannot be empty.")
            return ""
        car_id = f"CAR-{self.car_id_counter:03d}"
        self.cars[car_id] = {
            "model":            model_name.strip(),
            "condition":        100,
            "assigned_to_race": False,
        }
        self.car_id_counter += 1
        print(f"GARAGE: Added '{model_name}' (ID: {car_id})")
        return car_id

    def update_car_condition(self, car_id: str, damage_amount: int) -> bool:
        """Reduces a car's condition by damage_amount (clamped to 0 minimum)."""
        if car_id not in self.cars:
            print(f"FAIL [Inventory]: Car {car_id} not found in garage.")
            return False
        old = self.cars[car_id]["condition"]
        self.cars[car_id]["condition"] = max(0, old - damage_amount)
        new = self.cars[car_id]["condition"]
        status = "DESTROYED" if new == 0 else f"{new}%"
        print(f"GARAGE: {self.cars[car_id]['model']} condition "
              f"{old}% → {status}")
        return True

    def repair_car(self, car_id: str, repair_amount: int,
                   require_mechanic: bool = False,
                   crew_mod=None, mechanic_id: str = "") -> bool:
        """
        Restores condition by repair_amount.
        If require_mechanic=True, checks crew_mod for an available mechanic.
        """
        if car_id not in self.cars:
            print(f"FAIL [Inventory]: Car {car_id} not found.")
            return False

        if require_mechanic:
            if crew_mod is None:
                print("FAIL [Inventory]: crew_mod required for mechanic check.")
                return False
            mdata = crew_mod.get_member_skills(mechanic_id)
            if not mdata or mdata["role"] != "mechanic":
                print(f"FAIL [Inventory]: {mechanic_id} is not a mechanic.")
                return False
            if not crew_mod.is_available(mechanic_id):
                print(f"FAIL [Inventory]: Mechanic {mechanic_id} is not available.")
                return False

        old = self.cars[car_id]["condition"]
        self.cars[car_id]["condition"] = min(100, old + repair_amount)
        new = self.cars[car_id]["condition"]
        print(f"REPAIR: {self.cars[car_id]['model']} condition {old}% → {new}%")
        return True

    def set_car_race_status(self, car_id: str, assigned: bool) -> bool:
        if car_id not in self.cars:
            return False
        self.cars[car_id]["assigned_to_race"] = assigned
        return True

    def get_available_cars(self) -> dict:
        """Returns cars with condition > 20% that are not already assigned to a race."""
        return {cid: data for cid, data in self.cars.items()
                if data["condition"] > 20 and not data["assigned_to_race"]}

    def get_car(self, car_id: str) -> dict | None:
        return self.cars.get(car_id)

    def add_part(self, part_name: str, quantity: int) -> None:
        if quantity <= 0:
            print("FAIL [Inventory]: Quantity must be positive.")
            return
        self.parts[part_name] = self.parts.get(part_name, 0) + quantity
        print(f"PARTS: Added {quantity}x '{part_name}'. "
              f"Total: {self.parts[part_name]}")

    def use_part(self, part_name: str, quantity: int) -> bool:
        if self.parts.get(part_name, 0) < quantity:
            print(f"FAIL [Inventory]: Not enough '{part_name}'. "
                  f"Have: {self.parts.get(part_name, 0)}, Need: {quantity}")
            return False
        self.parts[part_name] -= quantity
        print(f"PARTS: Used {quantity}x '{part_name}'. "
              f"Remaining: {self.parts[part_name]}")
        return True

    def part_count(self, part_name: str) -> int:
        return self.parts.get(part_name, 0)

    def add_tool(self, tool_name: str) -> None:
        self.tools.add(tool_name.strip())
        print(f"TOOLS: Acquired '{tool_name}'.")

    def has_tool(self, tool_name: str) -> bool:
        return tool_name.strip() in self.tools

    def get_inventory_report(self) -> dict:
        return {
            "Cash":  self.cash_balance,
            "Cars":  self.cars,
            "Parts": self.parts,
            "Tools": sorted(self.tools),
        }

    def summary(self) -> None:
        print("\n=== Inventory Summary ===")
        print(f"  Cash: ${self.cash_balance}")
        print(f"  Cars ({len(self.cars)}):")
        for cid, data in self.cars.items():
            flag = "⚠ IN RACE" if data["assigned_to_race"] else ""
            print(f"    {cid} | {data['model']:<28} | {data['condition']}% {flag}")
        print(f"  Parts: {self.parts or 'None'}")
        print(f"  Tools: {sorted(self.tools) or 'None'}")
        print()
