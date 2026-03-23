"""
Race Management Module
-----------------------
Creates race events and handles driver / car entry validation.

Depends on: CrewManagementModule, InventoryModule
"""

from crewManagement import CrewManagementModule
from inventory import InventoryModule

VALID_DIFFICULTIES = {"easy", "medium", "hard", "extreme"}


class RaceManagementModule:

    def __init__(self, crew_mod: CrewManagementModule, inventory_mod: InventoryModule):
        self.crew_mod      = crew_mod
        self.inventory_mod = inventory_mod
        # {race_id: {"name": str, "difficulty": str, "prize_money": int,
        #             "participants": [{"driver_id": str, "car_id": str}],
        #             "status": "Open" | "In Progress" | "Completed"}}
        self.races:        dict = {}
        self.race_counter: int  = 1

    def create_race(self, name: str, difficulty_level: str,
                    prize_money: int) -> str | None:
        """Creates a new race event.  Returns race_id or None on failure."""
        if not name or not name.strip():
            print("FAIL [Race]: Race name cannot be empty.")
            return None
        diff = difficulty_level.strip().lower()
        if diff not in VALID_DIFFICULTIES:
            print(f"FAIL [Race]: Invalid difficulty '{difficulty_level}'. "
                  f"Choose from: {sorted(VALID_DIFFICULTIES)}")
            return None
        if prize_money < 0:
            print("FAIL [Race]: Prize money cannot be negative.")
            return None

        race_id = f"RACE-{self.race_counter:03d}"
        self.races[race_id] = {
            "name":         name.strip(),
            "difficulty":   diff,
            "prize_money":  prize_money,
            "participants": [],
            "status":       "Open",
        }
        self.race_counter += 1
        print(f"RACE CREATED: '{name}' (ID: {race_id}) | "
              f"Difficulty: {diff.capitalize()} | Prize: ${prize_money}")
        return race_id

    def enter_racer(self, race_id: str, driver_id: str, car_id: str) -> bool:
        """
        Validates and enters a driver + car into a race.
        Rules:
          • Race must exist and be Open
          • driver_id must be an active, available Driver in CrewManagement
          • car_id must be in available cars (condition > 20%, not already racing)
          • A driver may only enter once per race
        """
        # race checks
        if race_id not in self.races:
            print(f"FAIL [Race]: Race {race_id} does not exist.")
            return False
        race = self.races[race_id]
        if race["status"] != "Open":
            print(f"FAIL [Race]: Race {race_id} is '{race['status']}' "
                  f"and no longer accepting entries.")
            return False

        # driver checks
        driver_data = self.crew_mod.get_member_skills(driver_id)
        if not driver_data:
            print(f"FAIL [Race]: {driver_id} not found in Crew Management.")
            return False
        if driver_data["role"] != "driver":
            print(f"FAIL [Race]: {driver_id} is a "
                  f"'{driver_data['role'].capitalize()}', not a Driver.")
            return False
        if not self.crew_mod.is_available(driver_id):
            print(f"FAIL [Race]: Driver {driver_id} is currently unavailable.")
            return False
        if not self.crew_mod.registration_mod.is_active(driver_id):
            print(f"FAIL [Race]: Driver {driver_id} is Inactive.")
            return False

        # duplicate entry check
        if any(p["driver_id"] == driver_id for p in race["participants"]):
            print(f"FAIL [Race]: Driver {driver_id} is already entered in {race_id}.")
            return False

        # car checks
        available_cars = self.inventory_mod.get_available_cars()
        if car_id not in available_cars:
            print(f"FAIL [Race]: Car {car_id} is unavailable "
                  f"(condition ≤ 20% or already in a race).")
            return False

        # lock driver + car
        self.crew_mod.set_availability(driver_id, False)
        self.inventory_mod.set_car_race_status(car_id, True)

        race["participants"].append({"driver_id": driver_id, "car_id": car_id})
        car_name = available_cars[car_id]["model"]
        print(f"ENTRY: Driver {driver_id} → '{race['name']}' "
              f"driving {car_name} (ID: {car_id}).")
        return True

    def start_race(self, race_id: str) -> bool:
        """Moves race from Open → In Progress (requires at least 1 participant)."""
        if race_id not in self.races:
            print(f"FAIL [Race]: Race {race_id} not found.")
            return False
        race = self.races[race_id]
        if race["status"] != "Open":
            print(f"FAIL [Race]: Cannot start race in '{race['status']}' state.")
            return False
        if not race["participants"]:
            print(f"FAIL [Race]: Cannot start race with no participants.")
            return False
        race["status"] = "In Progress"
        print(f"RACE STARTED: '{race['name']}' (ID: {race_id}) — "
              f"{len(race['participants'])} participant(s).")
        return True

    def get_race_details(self, race_id: str) -> dict | None:
        return self.races.get(race_id)

    def list_open_races(self) -> list[str]:
        return [rid for rid, r in self.races.items() if r["status"] == "Open"]

    def summary(self) -> None:
        print("\n=== Race Management Summary ===")
        for rid, race in self.races.items():
            parts = len(race["participants"])
            print(f"  {rid} | {race['name']:<25} | "
                  f"{race['difficulty'].capitalize():<8} | "
                  f"${race['prize_money']:<6} | "
                  f"{race['status']:<12} | {parts} participant(s)")
        print()
