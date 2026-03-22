class RaceManagementModule:
    def __init__(self, crew_mod, inventory_mod):
        self.crew_mod = crew_mod
        self.inventory_mod = inventory_mod
        
        # Format: {race_id: {"name": "Midnight Run", "prize": 5000, "participants": []}}
        self.races = {}
        self.race_counter = 1

    def create_race(self, name, difficulty_level, prize_money):
        """Creates a new race event."""
        race_id = f"RACE-{self.race_counter:03d}"
        self.races[race_id] = {
            "name": name,
            "difficulty": difficulty_level,
            "prize_money": prize_money,
            "participants": [] # Will hold dicts of {"driver_id": id, "car_id": id}
        }
        self.race_counter += 1
        print(f"RACE CREATED: '{name}' (ID: {race_id}) - Prize: ${prize_money}")
        return race_id

    def enter_racer(self, race_id, driver_id, car_id):
        """Validates and enters a driver and car into a race."""
        if race_id not in self.races:
            print(f"FAIL: Race {race_id} does not exist.")
            return False

        driver_data = self.crew_mod.get_member_skills(driver_id)
        if not driver_data:
            print(f"FAIL: Driver {driver_id} not found in Crew Management.")
            return False
            
        if driver_data["role"] != "driver":
            print(f"FAIL: Member {driver_id} is a '{driver_data['role']}', not a Driver. Cannot race.")
            return False

        available_cars = self.inventory_mod.get_available_cars()
        if car_id not in available_cars:
            print(f"FAIL: Car {car_id} is either destroyed or does not exist in Inventory.")
            return False

        # If both checks pass, enter them into the race
        self.races[race_id]["participants"].append({
            "driver_id": driver_id,
            "car_id": car_id
        })
        
        # Let's get the car model name for a nice output
        car_name = available_cars[car_id]["model"]
        print(f"ENTRY SUCCESS: Driver {driver_id} entered into '{self.races[race_id]['name']}' driving a {car_name}.")
        return True

    def get_race_details(self, race_id):
        return self.races.get(race_id, None)