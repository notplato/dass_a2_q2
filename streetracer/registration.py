"""
Registration Module
-------------------
Handles crew member registration, lookup, status updates,
and basic roster reporting. All other modules depend on this
as the single source of truth for who is in the system.
"""

VALID_ROLES = {"driver", "mechanic", "strategist"}

class RegistrationModule:
    def __init__(self):
        # {member_id: {"name": str, "role": str, "status": str, "registered_at": int}}
        self.registry: dict = {}
        self.id_counter: int = 1

    def register_member(self, name, role):
        """
        Registers a new crew member.
        Returns the unique member_id.
        """
        name = name.strip() if name else ""
        role = role.strip().lower() if role else ""

        if not name or not role:
            print("FAIL [Registration]: Name and role are required.")
            return None
        
        if role not in VALID_ROLES:
            print(f"FAIL [Registration]: '{role}' is not a valid role. "
                  f"Choose from: {sorted(VALID_ROLES)}")
            return None

        
        member_id = f"CREW-{self.id_counter:03d}"
        self.registry[member_id] = {
            "name": name,
            "role": role,
            "status": "Active",
            "registered_at": self.id_counter,
        }

        self.id_counter += 1
        print(f"SUCCESS [Registration]: '{name}' registered as {role.capitalize()} "
              f"(ID: {member_id})")
        return member_id

    def get_member(self, member_id: str) -> dict | None:
        """Returns member details dict if they exist, else None."""
        return self.registry.get(member_id)
    
    def deactivate_member(self, member_id: str) -> bool:
        """Marks a member as Inactive (soft-delete)."""
        member = self.registry.get(member_id)
        if not member:
            print(f"FAIL [Registration]: Member {member_id} not found.")
            return False
        if member["status"] == "Inactive":
            print(f"INFO [Registration]: Member {member_id} is already Inactive.")
            return False
        member["status"] = "Inactive"
        print(f"INFO [Registration]: {member['name']} ({member_id}) set to Inactive.")
        return True

    def reactivate_member(self, member_id: str) -> bool:
        """Re-activates an Inactive member."""
        member = self.registry.get(member_id)
        if not member:
            print(f"FAIL [Registration]: Member {member_id} not found.")
            return False
        if member["status"] == "Active":
            print(f"INFO [Registration]: Member {member_id} is already Active.")
            return False
        member["status"] = "Active"
        print(f"INFO [Registration]: {member['name']} ({member_id}) reactivated.")
        return True

    def is_active(self, member_id: str) -> bool:
        """Convenience check: True only if member exists and is Active."""
        m = self.registry.get(member_id)
        return bool(m and m["status"] == "Active")

    def list_all_members(self) -> dict:
        return dict(self.registry)

    def list_active_members(self) -> dict:
        return {mid: data for mid, data in self.registry.items()
                if data["status"] == "Active"}

    def get_members_by_role(self, role: str) -> dict:
        role = role.lower()
        return {mid: data for mid, data in self.registry.items()
                if data["role"] == role and data["status"] == "Active"}

    def summary(self) -> None:
        """Prints a quick roster summary to stdout."""
        total = len(self.registry)
        active = sum(1 for d in self.registry.values() if d["status"] == "Active")
        print(f"\n=== Registration Summary: {active} active / {total} total ===")
        for mid, data in self.registry.items():
            flag = "✓" if data["status"] == "Active" else "✗"
            print(f"  [{flag}] {mid} | {data['name']:<20} | {data['role'].capitalize()}")
        print()
