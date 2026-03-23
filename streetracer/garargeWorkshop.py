"""
Garage Workshop Module  (Additional Module #2)
------------------------------------------------
Provides repair and upgrade services for cars in the garage.

Depends on: InventoryModule, CrewManagementModule
"""

from inventory import InventoryModule
from crewManagement import CrewManagementModule

# cost per condition point restored
REPAIR_COST_PER_POINT = 20   # $20 per 1% condition

UPGRADES: dict[str, dict] = {
    "turbo_kit": {
        "description": "Increases top-speed rating",
        "required_part": "Turbocharger",
        "part_qty":       1,
        "cash_cost":     1500,
        "attribute":     "speed",
        "bonus":          10,
        "max_level":       3,
    },
    "racing_tyres": {
        "description": "Improves handling & grip",
        "required_part": "Racing Slicks",
        "part_qty":       4,
        "cash_cost":      800,
        "attribute":     "handling",
        "bonus":          8,
        "max_level":       2,
    },
    "roll_cage": {
        "description": "Increases durability (reduces race damage)",
        "required_part": None,
        "part_qty":       0,
        "cash_cost":     1200,
        "attribute":     "durability",
        "bonus":          5,
        "max_level":       2,
    },
}


class GarageWorkshopModule:

    def __init__(self, inventory_mod: InventoryModule,
                 crew_mod: CrewManagementModule):
        self.inventory_mod = inventory_mod
        self.crew_mod      = crew_mod
        # {car_id: {"upgrades": {upgrade_key: level}, "attributes": {...}}}
        self.car_workshop_data: dict = {}
        self.repair_log:        list = []

    def _ensure_car_data(self, car_id: str) -> bool:
        """Lazily creates workshop data entry for a car."""
        if self.inventory_mod.get_car(car_id) is None:
            print(f"FAIL [Workshop]: Car {car_id} not found in Inventory.")
            return False
        if car_id not in self.car_workshop_data:
            self.car_workshop_data[car_id] = {
                "upgrades":   {},
                "attributes": {"speed": 50, "handling": 50, "durability": 50},
            }
        return True

    def _find_available_mechanic(self) -> str | None:
        """Returns first available mechanic_id, or None."""
        mechanics = self.crew_mod.get_available_by_role("mechanic")
        return mechanics[0] if mechanics else None

    def repair_car(self, car_id: str,
                   mechanic_id: str | None = None,
                   target_condition: int = 100) -> bool:
        """
        Repairs a car to target_condition (default 100%).
        Automatically finds an available mechanic if mechanic_id is None.
        Charges repair cost from inventory cash.

        Cost = (condition points restored) x REPAIR_COST_PER_POINT
        """
        if not self._ensure_car_data(car_id):
            return False

        car = self.inventory_mod.get_car(car_id)
        current = car["condition"]

        if current >= target_condition:
            print(f"INFO [Workshop]: {car['model']} is already at "
                  f"{current}% — no repair needed.")
            return True

        # find mechanic
        mech_id = mechanic_id or self._find_available_mechanic()
        if not mech_id:
            print("FAIL [Workshop]: No available mechanic found.")
            return False

        mdata = self.crew_mod.get_member_skills(mech_id)
        if not mdata or mdata["role"] != "mechanic":
            print(f"FAIL [Workshop]: {mech_id} is not a mechanic.")
            return False
        if not self.crew_mod.is_available(mech_id):
            print(f"FAIL [Workshop]: Mechanic {mech_id} is currently busy.")
            return False

        points_to_repair = min(target_condition, 100) - current
        cost = points_to_repair * REPAIR_COST_PER_POINT

        if not self.inventory_mod.update_cash(
                -cost, reason=f"Repair {car_id} by {points_to_repair}pts"):
            return False   # insufficient funds

        # mark mechanic busy during repair, then release
        self.crew_mod.set_availability(mech_id, False)
        self.inventory_mod.repair_car(car_id, points_to_repair)
        self.crew_mod.set_availability(mech_id, True)

        # Skill gain for mechanic
        self.crew_mod.increment_skill(mech_id, "repair_speed", 2)

        self.repair_log.append({
            "car_id":     car_id,
            "mechanic":   mech_id,
            "points":     points_to_repair,
            "cost":       cost,
        })

        mname = self.crew_mod.registration_mod.get_member(mech_id)["name"]
        print(f"REPAIR DONE: {car['model']} restored by {points_to_repair}pts. "
              f"Cost: ${cost}. Mechanic: {mname}.")
        return True

    def install_upgrade(self, car_id: str, upgrade_key: str,
                        mechanic_id: str | None = None) -> bool:
        """
        Installs an upgrade on a car.
        Validates: car exists, upgrade valid, mechanic available,
                   max level not exceeded, cash & parts sufficient.
        """
        if not self._ensure_car_data(car_id):
            return False

        upgrade_key = upgrade_key.lower().strip().replace(" ", "_")
        if upgrade_key not in UPGRADES:
            print(f"FAIL [Workshop]: Unknown upgrade '{upgrade_key}'. "
                  f"Available: {list(UPGRADES.keys())}")
            return False

        spec     = UPGRADES[upgrade_key]
        car_data = self.car_workshop_data[car_id]
        current_level = car_data["upgrades"].get(upgrade_key, 0)

        if current_level >= spec["max_level"]:
            print(f"FAIL [Workshop]: '{upgrade_key}' is already at "
                  f"max level ({spec['max_level']}) on this car.")
            return False

        # mechanic
        mech_id = mechanic_id or self._find_available_mechanic()
        if not mech_id:
            print("FAIL [Workshop]: No available mechanic.")
            return False
        mdata = self.crew_mod.get_member_skills(mech_id)
        if not mdata or mdata["role"] != "mechanic":
            print(f"FAIL [Workshop]: {mech_id} is not a mechanic.")
            return False
        if not self.crew_mod.is_available(mech_id):
            print(f"FAIL [Workshop]: Mechanic {mech_id} is busy.")
            return False

        # cash
        if not self.inventory_mod.update_cash(
                -spec["cash_cost"],
                reason=f"Upgrade {upgrade_key} on {car_id}"):
            return False

        # parts
        if spec["required_part"]:
            if not self.inventory_mod.use_part(
                    spec["required_part"], spec["part_qty"]):
                # refund cash
                self.inventory_mod.update_cash(
                    spec["cash_cost"],
                    reason=f"Refund failed upgrade {upgrade_key}")
                return False

        # apply upgrade
        car_data["upgrades"][upgrade_key] = current_level + 1
        attr = spec["attribute"]
        car_data["attributes"][attr] = min(
            100, car_data["attributes"][attr] + spec["bonus"])

        car = self.inventory_mod.get_car(car_id)
        mname = self.crew_mod.registration_mod.get_member(mech_id)["name"]
        print(f"UPGRADE: '{upgrade_key}' installed on {car['model']} "
              f"(Level {current_level + 1}/{spec['max_level']}). "
              f"{attr.capitalize()} → {car_data['attributes'][attr]}. "
              f"Mechanic: {mname}.")
        return True

    def get_car_workshop_data(self, car_id: str) -> dict | None:
        return self.car_workshop_data.get(car_id)

    def get_damage_reduction(self, car_id: str) -> int:
        """Returns damage reduction % from durability upgrades."""
        data = self.car_workshop_data.get(car_id)
        if not data:
            return 0
        durability = data["attributes"].get("durability", 50)
        # every 10 points above 50 gives 1% damage reduction
        return max(0, (durability - 50) // 10)

    def summary(self) -> None:
        print("\n=== Garage Workshop ===")
        if not self.car_workshop_data:
            print("  No cars in workshop records.")
        for car_id, data in self.car_workshop_data.items():
            car = self.inventory_mod.get_car(car_id)
            model = car["model"] if car else car_id
            attrs = data["attributes"]
            upgrades = data["upgrades"] or "None"
            print(f"  {car_id} | {model:<28} | "
                  f"SPD:{attrs['speed']} HDL:{attrs['handling']} "
                  f"DUR:{attrs['durability']} | Upgrades: {upgrades}")
        print()
