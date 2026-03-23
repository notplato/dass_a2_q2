import pytest

@pytest.mark.parametrize("inv", [1000], indirect=True)
def test_register_then_race_full_flow(reg, crew, inv, race, res):
    mid = reg.register_member("Xena", "driver")
    crew.assign_role(mid, "driver")
    crew.update_skill(mid, "reflexes", 60)
    cid = inv.add_car("Porsche 911")
    rid = race.create_race("Grand Prix", "medium", 8000)
    race.enter_racer(rid, mid, cid)
    res.process_race_results(rid, mid)

    assert inv.cash_balance == 9000, f"Expected 9000, got {inv.cash_balance}"
    assert crew.is_available(mid), "Driver should be free"
    assert inv.get_car(cid)["condition"] == 80, "Medium race: 20 damage"

@pytest.mark.parametrize("inv", [50000], indirect=True)
def test_mechanic_required_after_race_damage(reg, crew, inv, race, res, mis, rep, ws):
    # set up driver
    driver_id = reg.register_member("Yuri", "driver")
    crew.assign_role(driver_id, "driver")

    # set up mechanic
    mech_id = reg.register_member("Zara", "mechanic")
    crew.assign_role(mech_id, "mechanic")

    # add a car and damage it heavily
    cid = inv.add_car("Chevrolet Camaro")
    inv.update_car_condition(cid, 85)   # condition: 15% — below threshold

    # attempt to enter race with damaged car
    rid = race.create_race("Damage Test", "easy", 500)
    ok  = race.enter_racer(rid, driver_id, cid)
    assert not ok, "Damaged car should be rejected"

    # repair the car via workshop
    repair_ok = ws.repair_car(cid, mechanic_id=mech_id, target_condition=80)
    assert repair_ok, "Repair should succeed"
    assert inv.get_car(cid)["condition"] == 80

    # now enter should succeed
    ok2 = race.enter_racer(rid, driver_id, cid)
    assert ok2, "Repaired car should now be accepted"


def test_busy_driver_cannot_race(reg, crew, inv, race, res, mis):
    mid = reg.register_member("Aaron", "driver")
    crew.assign_role(mid, "driver")
    crew.set_availability(mid, False)    # simulate busy (e.g. mid-mission)

    cid = inv.add_car("BMW M3")
    rid = race.create_race("Busy Test", "easy", 1000)
    ok  = race.enter_racer(rid, mid, cid)
    assert not ok, "Busy driver should be rejected from race"

@pytest.mark.parametrize("inv", [0], indirect=True)
def test_race_result_updates_leaderboard_and_cash(reg, crew, inv, race, res):
    mid = reg.register_member("Bella", "driver")
    crew.assign_role(mid, "driver")
    cid = inv.add_car("Lamborghini Gallardo")
    rid = race.create_race("Cash Check", "hard", 10_000)
    race.enter_racer(rid, mid, cid)
    res.process_race_results(rid, mid)

    assert inv.cash_balance == 10_000
    board = res.get_leaderboard()
    assert board[0][0] == mid and board[0][1] == 1

@pytest.mark.parametrize("inv", [0], indirect=True)
def test_multi_role_mission_requires_all_roles(reg, crew, inv, mis):
    d = reg.register_member("Cam", "driver")
    s = reg.register_member("Dana", "strategist")
    crew.assign_role(d, "driver")
    crew.assign_role(s, "strategist")

    msn = mis.create_mission("Route Hack", "sabotage",
                             {"driver": 1, "strategist": 1}, reward=4000)

    # only driver, should fail
    ok1 = mis.assign_and_execute_mission(msn, [d])
    assert not ok1, "Only driver — should fail"

    # both roles, should succeed
    ok2 = mis.assign_and_execute_mission(msn, [d, s])
    assert ok2, "Driver + Strategist — should succeed"
    assert inv.cash_balance == 4000


def test_car_assigned_to_race_not_available_for_second(reg, crew, inv, race):
    d1 = reg.register_member("Eli", "driver")
    d2 = reg.register_member("Fay", "driver")
    crew.assign_role(d1, "driver")
    crew.assign_role(d2, "driver")

    cid  = inv.add_car("Shared Car")
    rid1 = race.create_race("Race 1", "easy", 100)
    rid2 = race.create_race("Race 2", "easy", 100)

    race.enter_racer(rid1, d1, cid)   # car now assigned
    ok = race.enter_racer(rid2, d2, cid)
    assert not ok, "Car already in a race should not be assignable again"
