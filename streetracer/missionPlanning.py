"""
Mission Planning Module
------------------------
Creates, assigns, and executes missions (delivery, rescue, heist, etc.).
Verifies required roles are filled by available crew members before
a mission may begin.  On success, deposits the reward to inventory
and marks participants busy → available.

Depends on: CrewManagementModule, InventoryModule
"""

from crewManagement import CrewManagementModule
from inventory import InventoryModule

VALID_MISSION_TYPES = {"delivery", "rescue", "heist", "surveillance", "sabotage"}


class MissionPlanningModule:

    def __init__(self, crew_mod: CrewManagementModule,
                 inventory_mod: InventoryModule):
        self.crew_mod      = crew_mod
        self.inventory_mod = inventory_mod
        # {mission_id: {...}}
        self.missions:        dict = {}
        self.mission_counter: int  = 1

    def create_mission(self, name: str, mission_type: str,
                       required_roles: dict[str, int],
                       reward: int,
                       required_parts: dict[str, int] | None = None) -> str | None:
        """
        Creates a mission on the board.

        `required_roles`  — {"driver": 1, "mechanic": 2}
        `required_parts`  — {"Turbocharger": 1} (optional)
        Returns mission_id or None on validation failure.
        """
        if not name or not name.strip():
            print("FAIL [Mission]: Mission name cannot be empty.")
            return None
        mtype = mission_type.strip().lower()
        if mtype not in VALID_MISSION_TYPES:
            print(f"FAIL [Mission]: Invalid type '{mission_type}'. "
                  f"Choose from: {sorted(VALID_MISSION_TYPES)}")
            return None
        if reward < 0:
            print("FAIL [Mission]: Reward cannot be negative.")
            return None
        if not required_roles:
            print("FAIL [Mission]: At least one required role must be specified.")
            return None

        mission_id = f"MSN-{self.mission_counter:03d}"
        self.missions[mission_id] = {
            "name":           name.strip(),
            "type":           mtype,
            "required_roles": required_roles,
            "required_parts": required_parts or {},
            "reward":         reward,
            "status":         "Available",
            "assigned_crew":  [],
        }
        self.mission_counter += 1

        roles_str = ", ".join(
            f"{k.capitalize()} ×{v}" for k, v in required_roles.items())
        print(f"MISSION: '{name}' [{mtype}] created (ID: {mission_id}). "
              f"Requires: {roles_str} | Reward: ${reward}")
        return mission_id

    def assign_and_execute_mission(self, mission_id: str,
                                   assigned_member_ids: list[str]) -> bool:
        """
        Verifies assigned crew meets required roles (and quantity),
        checks part availability, executes mission, pays reward.
        """
        if mission_id not in self.missions:
            print(f"FAIL [Mission]: Mission {mission_id} does not exist.")
            return False

        mission = self.missions[mission_id]
        if mission["status"] != "Available":
            print(f"FAIL [Mission]: Mission {mission_id} is "
                  f"'{mission['status']}' — cannot re-run.")
            return False

        print(f"\n--- Planning: {mission['name']} ({mission_id}) ---")

        for mid in assigned_member_ids:
            crew_data = self.crew_mod.get_member_skills(mid)
            if not crew_data:
                print(f"FAIL [Mission]: {mid} is not in Crew Management.")
                return False
            if not self.crew_mod.registration_mod.is_active(mid):
                print(f"FAIL [Mission]: {mid} is Inactive.")
                return False
            if not self.crew_mod.is_available(mid):
                print(f"FAIL [Mission]: {mid} is currently busy.")
                return False

        provided_roles: dict[str, int] = {}
        for mid in assigned_member_ids:
            role = self.crew_mod.get_member_skills(mid)["role"]
            provided_roles[role] = provided_roles.get(role, 0) + 1

        for req_role, req_count in mission["required_roles"].items():
            provided = provided_roles.get(req_role, 0)
            if provided < req_count:
                print(f"FAIL [Mission]: Need {req_count} {req_role.capitalize()}(s), "
                      f"only {provided} assigned.")
                return False

        for part, qty in mission["required_parts"].items():
            if self.inventory_mod.part_count(part) < qty:
                print(f"FAIL [Mission]: Need {qty}x '{part}', "
                      f"only {self.inventory_mod.part_count(part)} available.")
                return False
        for part, qty in mission["required_parts"].items():
            self.inventory_mod.use_part(part, qty)

        for mid in assigned_member_ids:
            self.crew_mod.set_availability(mid, False)

        print("SUCCESS [Mission]: All checks passed. Executing…")
        self.inventory_mod.update_cash(
            mission["reward"], reason=f"Mission: {mission['name']}")

        for mid in assigned_member_ids:
            self.crew_mod.record_mission_completion(mid)
            self.crew_mod.set_availability(mid, True)

        mission["status"]        = "Completed"
        mission["assigned_crew"] = list(assigned_member_ids)

        print(f"DONE [Mission]: '{mission['name']}' completed. "
              f"${mission['reward']} deposited.")
        return True

    def get_mission(self, mission_id: str) -> dict | None:
        return self.missions.get(mission_id)

    def list_available_missions(self) -> list[str]:
        return [mid for mid, m in self.missions.items()
                if m["status"] == "Available"]

    def summary(self) -> None:
        print("\n=== Mission Board ===")
        for mid, m in self.missions.items():
            roles_str = ", ".join(
                f"{k.capitalize()}×{v}" for k, v in m["required_roles"].items())
            print(f"  {mid} | {m['name']:<25} | {m['type']:<12} | "
                  f"${m['reward']:<6} | {m['status']:<10} | {roles_str}")
        print()
