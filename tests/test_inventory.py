import pytest

@pytest.mark.parametrize("inv", [1000], indirect=True)
def test_cash_operations(inv):
    inv.update_cash(500, "prize")
    assert inv.cash_balance == 1500
    inv.update_cash(-200, "parts")
    assert inv.cash_balance == 1300
    ok = inv.update_cash(-2000, "overdraft attempt")
    assert not ok, "Overdraft should be blocked"
    assert inv.cash_balance == 1300, "Balance unchanged on failed transaction"

def test_car_add_and_condition(inv):
    cid = inv.add_car("Nissan Skyline R34")
    assert cid.startswith("CAR-")
    assert inv.get_car(cid)["condition"] == 100
    inv.update_car_condition(cid, 30)
    assert inv.get_car(cid)["condition"] == 70
    inv.update_car_condition(cid, 200)      # excess damage
    assert inv.get_car(cid)["condition"] == 0, "Condition should not go below 0"

def test_available_cars_filter(inv):
    c1 = inv.add_car("Toyota Supra")
    c2 = inv.add_car("Honda NSX")
    inv.update_car_condition(c2, 90)      # drops to 10% → below threshold
    available = inv.get_available_cars()
    assert c1 in available, "Good car should be available"
    assert c2 not in available, "Damaged car should not be available"

def test_parts_use_and_fail(inv):
    inv.add_part("Turbocharger", 2)
    ok = inv.use_part("Turbocharger", 1)
    assert ok and inv.part_count("Turbocharger") == 1
    ok = inv.use_part("Turbocharger", 5)
    assert not ok, "Should fail — only 1 left"
    assert inv.part_count("Turbocharger") == 1, "Count unchanged on failure"
