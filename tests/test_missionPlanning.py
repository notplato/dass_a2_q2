import pytest

@pytest.mark.parametrize("inv", [0], indirect=True)
def test_create_and_complete_mission(reg, crew, inv, mis):
    mid = reg.register_member("Sam", "driver")
    crew.assign_role(mid, "driver")
    msn = mis.create_mission("Package Run", "delivery",
                             {"driver": 1}, reward=2000)
    ok  = mis.assign_and_execute_mission(msn, [mid])
    assert ok
    assert inv.cash_balance == 2000
    assert mis.get_mission(msn)["status"] == "Completed"

@pytest.mark.parametrize("inv", [500], indirect=True)
def test_mission_missing_role(reg, crew, inv, mis):
    m1 = reg.register_member("Tina", "mechanic")
    crew.assign_role(m1, "mechanic")
    msn = mis.create_mission("Engine Swap", "heist",
                             {"mechanic": 2}, reward=3000)
    ok  = mis.assign_and_execute_mission(msn, [m1])
    assert not ok, "Single mechanic should not satisfy 2-mechanic requirement"
    assert inv.cash_balance == 500, "Cash should be untouched"


def test_mission_requires_parts(reg, crew, inv, mis):
    mid = reg.register_member("Uma", "mechanic")
    crew.assign_role(mid, "mechanic")
    inv.add_part("Turbocharger", 1)
    msn = mis.create_mission("Turbo Swap", "delivery",
                             {"mechanic": 1},
                             reward=1500,
                             required_parts={"Turbocharger": 2})
    ok  = mis.assign_and_execute_mission(msn, [mid])
    assert not ok, "Should fail — only 1 Turbocharger available"
    assert inv.part_count("Turbocharger") == 1, "Parts should not be consumed on failure"


def test_mission_with_inactive_member(reg, crew, inv, mis):
    mid = reg.register_member("Victor", "strategist")
    crew.assign_role(mid, "strategist")
    reg.deactivate_member(mid)
    msn = mis.create_mission("Recon", "surveillance",
                             {"strategist": 1}, reward=1000)
    ok  = mis.assign_and_execute_mission(msn, [mid])
    assert not ok, "Inactive member should block mission"


def test_mission_already_completed(reg, crew, inv, mis):
    mid = reg.register_member("Wendy", "driver")
    crew.assign_role(mid, "driver")
    msn = mis.create_mission("Quick Delivery", "delivery",
                             {"driver": 1}, reward=500)
    mis.assign_and_execute_mission(msn, [mid])
    ok = mis.assign_and_execute_mission(msn, [mid])
    assert not ok, "Completed mission should not be re-run"
