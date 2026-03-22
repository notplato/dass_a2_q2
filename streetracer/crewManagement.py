class CrewManagementModule:
    ROLE_SKILLS = {
        "driver": ["cornering", "reflexes", "throttle_control"],
        "mechanic": ["engine_tuning", "diagnostics", "repair_speed"],
        "strategist": ["route_planning", "weather_analysis", "resource_management"]
    }

    def __init__(self, registration_mod):
        self.registration_mod = registration_mod
        self.crew_details = {}

    def assign_role(self, member_id, role):
        """Assigns a role and initializes their specific skill set to 0."""
        member = self.registration_mod.get_member(member_id)
        if not member:
            print(f"FAIL: Cannot assign role. Member {member_id} not found in Registration.")
            return False

        role_lower = role.lower()
        if role_lower not in self.ROLE_SKILLS:
            print(f"FAIL: '{role}' is an invalid role. Choose from: {list(self.ROLE_SKILLS.keys())}")
            return False

        initial_skills = {skill: 0 for skill in self.ROLE_SKILLS[role_lower]}

        self.crew_details[member_id] = {
            "role": role_lower,
            "skills": initial_skills
        }
        
        print(f"SUCCESS: {member['name']} assigned as {role.capitalize()}. Initialized skills: {list(initial_skills.keys())}")
        return True

    def update_skill(self, member_id, skill_name, new_value):
        """Updates a specific skill for a crew member, enforcing role restrictions."""
        if member_id not in self.crew_details:
            print(f"FAIL: Member {member_id} does not have an assigned role yet.")
            return False

        member_info = self.crew_details[member_id]
        role = member_info["role"]
        skill_lower = skill_name.lower()

        if skill_lower not in self.ROLE_SKILLS[role]:
            print(f"FAIL: A {role.capitalize()} does not possess the '{skill_name}' skill.")
            return False

        clamped_value = max(0, min(100, new_value))
        member_info["skills"][skill_lower] = clamped_value
        
        name = self.registration_mod.get_member(member_id)['name']
        print(f"UPDATE: {name}'s '{skill_name}' changed to {clamped_value}.")
        return True

    def get_member_skills(self, member_id):
        return self.crew_details.get(member_id, None)