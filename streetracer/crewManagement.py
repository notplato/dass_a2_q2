"""
Crew Management Module
-----------------------
Manages role assignments and per-role skill tracking for every
registered crew member.  Skills are clamped to [0, 100].

Depends on: RegistrationModule
"""

from registration import RegistrationModule

ROLE_SKILLS: dict[str, list[str]] = {
    "driver":     ["cornering", "reflexes", "throttle_control", "stamina"],
    "mechanic":   ["engine_tuning", "diagnostics", "repair_speed", "part_efficiency"],
    "strategist": ["route_planning", "weather_analysis", "resource_management", "risk_assessment"],
}

VALID_ROLES = set(ROLE_SKILLS.keys())


class CrewManagementModule:

    def __init__(self, registration_mod: RegistrationModule):
        self.registration_mod = registration_mod
        # {member_id: {"role": str, "skills": {skill: int}, "missions_completed": int,
        #               "races_won": int, "available": bool}}
        self.crew_details: dict = {}

    def assign_role(self, member_id: str, role: str) -> bool:
        """
        Assigns a role to a registered, active member and initialises
        all role-specific skills to 0.
        """
        member = self.registration_mod.get_member(member_id)
        if not member:
            print(f"FAIL [Crew]: Member {member_id} not found in Registration.")
            return False
        if not self.registration_mod.is_active(member_id):
            print(f"FAIL [Crew]: Member {member_id} is Inactive and cannot be assigned a role.")
            return False

        role_lower = role.strip().lower()
        if role_lower not in VALID_ROLES:
            print(f"FAIL [Crew]: '{role}' is not a valid role. "
                  f"Choose from: {sorted(VALID_ROLES)}")
            return False

        # warn if re-assigning (skills reset)
        if member_id in self.crew_details:
            old_role = self.crew_details[member_id]["role"]
            print(f"INFO [Crew]: {member['name']} is being re-assigned "
                  f"from {old_role.capitalize()} → {role_lower.capitalize()}. Skills reset.")

        self.crew_details[member_id] = {
            "role":               role_lower,
            "skills":             {s: 0 for s in ROLE_SKILLS[role_lower]},
            "missions_completed": 0,
            "races_won":          0,
            "available":          True,   # True = not currently on a mission/race
        }
        print(f"SUCCESS [Crew]: {member['name']} assigned as {role_lower.capitalize()}. "
              f"Skills initialised: {list(ROLE_SKILLS[role_lower])}")
        return True

    def update_skill(self, member_id: str, skill_name: str, new_value: int) -> bool:
        """Updates one skill for a crew member (clamped to 0-100)."""
        if member_id not in self.crew_details:
            print(f"FAIL [Crew]: Member {member_id} has no assigned role yet.")
            return False

        info = self.crew_details[member_id]
        skill_lower = skill_name.strip().lower()

        if skill_lower not in ROLE_SKILLS[info["role"]]:
            print(f"FAIL [Crew]: A {info['role'].capitalize()} does not have "
                  f"the '{skill_name}' skill. "
                  f"Valid: {ROLE_SKILLS[info['role']]}")
            return False

        clamped = max(0, min(100, int(new_value)))
        info["skills"][skill_lower] = clamped
        name = self.registration_mod.get_member(member_id)["name"]
        print(f"UPDATE [Crew]: {name}'s '{skill_lower}' set to {clamped}.")
        return True

    def increment_skill(self, member_id: str, skill_name: str, delta: int = 5) -> bool:
        """Convenience: adds `delta` to an existing skill value."""
        info = self.crew_details.get(member_id)
        if not info:
            return False
        current = info["skills"].get(skill_name.lower(), None)
        if current is None:
            return False
        return self.update_skill(member_id, skill_name, current + delta)

    def set_availability(self, member_id: str, available: bool) -> bool:
        if member_id not in self.crew_details:
            return False
        self.crew_details[member_id]["available"] = available
        state = "Available" if available else "Busy"
        name = self.registration_mod.get_member(member_id)["name"]
        print(f"INFO [Crew]: {name} is now {state}.")
        return True

    def is_available(self, member_id: str) -> bool:
        info = self.crew_details.get(member_id)
        return bool(info and info["available"])

    def record_mission_completion(self, member_id: str) -> None:
        if member_id in self.crew_details:
            self.crew_details[member_id]["missions_completed"] += 1

    def record_race_win(self, member_id: str) -> None:
        if member_id in self.crew_details:
            self.crew_details[member_id]["races_won"] += 1

    def get_member_skills(self, member_id: str) -> dict | None:
        return self.crew_details.get(member_id)

    def get_available_by_role(self, role: str) -> list[str]:
        """Returns list of member_ids who are available and have the given role."""
        role = role.lower()
        return [mid for mid, info in self.crew_details.items()
                if info["role"] == role and info["available"]
                and self.registration_mod.is_active(mid)]

    def summary(self) -> None:
        print("\n=== Crew Management Summary ===")
        for mid, info in self.crew_details.items():
            member = self.registration_mod.get_member(mid)
            name = member["name"] if member else mid
            avail = "Available" if info["available"] else "Busy"
            skills_str = ", ".join(f"{k}={v}" for k, v in info["skills"].items())
            print(f"  {mid} | {name:<20} | {info['role'].capitalize():<12} "
                  f"| {avail:<10} | {skills_str}")
        print()
