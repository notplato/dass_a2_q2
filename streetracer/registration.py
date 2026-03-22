class RegistrationModule:
    def __init__(self):
        # stores members as {member_id: {"name": name, "role": role}}
        self.registry = {}
        self.id_counter = 1

    def register_member(self, name, role):
        """
        Registers a new crew member.
        Returns the unique member_id.
        """
        if not name or not role:
            print("Error: Name and role are required.")
            return None
        
        member_id = f"CREW-{self.id_counter:03d}"
        self.registry[member_id] = {
            "name": name,
            "role": role,
            "status": "Active"
        }
        
        self.id_counter += 1
        print(f"Successfully registered: {name} as {role} (ID: {member_id})")
        return member_id

    def get_member(self, member_id):
        """Returns member details if they exist."""
        return self.registry.get(member_id)

    def list_all_members(self):
        return self.registry