def test_assign_role_to_registered_member(reg, crew):
    mid = reg.register_member("Dave", "driver")
    ok  = crew.assign_role(mid, "driver")
    assert ok, "assign_role should succeed"
    info = crew.get_member_skills(mid)
    assert info is not None
    assert info["role"] == "driver"
    for skill in ("cornering", "reflexes", "throttle_control", "stamina"):
        assert skill in info["skills"], f"Missing skill: {skill}"
        assert info["skills"][skill] == 0

def test_assign_role_unregistered_member(reg, crew):
    ok = crew.assign_role("CREW-999", "driver")
    assert not ok, "Should fail for unregistered member"


def test_assign_role_inactive_member(reg, crew):
    mid = reg.register_member("Ghost", "mechanic")
    reg.deactivate_member(mid)
    ok = crew.assign_role(mid, "mechanic")
    assert not ok, "Inactive member should not be assignable"


def test_update_skill_valid(reg, crew):
    mid = reg.register_member("Fiona", "driver")
    crew.assign_role(mid, "driver")
    crew.update_skill(mid, "cornering", 75)
    assert crew.get_member_skills(mid)["skills"]["cornering"] == 75
    # test clamping
    crew.update_skill(mid, "cornering", 150)
    assert crew.get_member_skills(mid)["skills"]["cornering"] == 100, \
        "Skill should be clamped at 100"
    crew.update_skill(mid, "cornering", -10)
    assert crew.get_member_skills(mid)["skills"]["cornering"] == 0, \
        "Skill should be clamped at 0"


def test_update_wrong_role_skill(reg, crew):
    mid = reg.register_member("Greg", "driver")
    crew.assign_role(mid, "driver")
    ok = crew.update_skill(mid, "engine_tuning", 50)
    assert not ok, "Driver should not have engine_tuning"
