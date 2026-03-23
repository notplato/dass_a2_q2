import pytest

def test_basic_repair(reg, crew, inv, ws):
    mech = reg.register_member("Gus", "mechanic")
    crew.assign_role(mech, "mechanic")
    cid = inv.add_car("Repair Test Car")
    inv.update_car_condition(cid, 40)   # condition: 60%
    cash_before = inv.cash_balance

    ok = ws.repair_car(cid, mechanic_id=mech, target_condition=100)
    assert ok
    assert inv.get_car(cid)["condition"] == 100
    cost = 40 * 20   # 40 points × $20
    assert inv.cash_balance == cash_before - cost
    assert crew.is_available(mech), "Mechanic freed after repair"

@pytest.mark.parametrize("inv", [100], indirect=True)
def test_repair_insufficient_funds(reg, crew, inv, ws):
    mech = reg.register_member("Hal", "mechanic")
    crew.assign_role(mech, "mechanic")
    cid = inv.add_car("Broke Car")
    inv.update_car_condition(cid, 80)   # condition: 20%  → 80 pts repair needed = $1600

    ok = ws.repair_car(cid, mechanic_id=mech, target_condition=100)
    assert not ok, "Should fail — insufficient funds"
    assert inv.get_car(cid)["condition"] == 20, "Condition should be unchanged"

def test_install_upgrade(reg, crew, inv, ws):
    mech = reg.register_member("Iris", "mechanic")
    crew.assign_role(mech, "mechanic")
    cid = inv.add_car("Upgrade Test Car")
    inv.add_part("Turbocharger", 2)

    ok = ws.install_upgrade(cid, "turbo_kit", mechanic_id=mech)
    assert ok, "Upgrade should succeed"
    data = ws.get_car_workshop_data(cid)
    assert data["upgrades"].get("turbo_kit") == 1
    assert data["attributes"]["speed"] == 60, "50 + 10 = 60"
    assert inv.part_count("Turbocharger") == 1, "1 turbo consumed"

@pytest.mark.parametrize("inv", [50000], indirect=True)
def test_upgrade_max_level(reg, crew, inv, ws):
    mech = reg.register_member("Jak", "mechanic")
    crew.assign_role(mech, "mechanic")
    cid = inv.add_car("Max Level Car")
    inv.add_part("Racing Slicks", 20)

    ws.install_upgrade(cid, "racing_tyres", mechanic_id=mech)
    ws.install_upgrade(cid, "racing_tyres", mechanic_id=mech)
    ok = ws.install_upgrade(cid, "racing_tyres", mechanic_id=mech)
    assert not ok, "Should fail — already at max level 2"
