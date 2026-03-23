def test_create_race_valid(race):
    rid = race.create_race("Midnight Run", "hard", 5000)
    assert rid is not None and rid.startswith("RACE-")

def test_enter_valid_driver(reg, crew, inv, race):
    mid = reg.register_member("Hannah", "driver")
    crew.assign_role(mid, "driver")
    cid = inv.add_car("Mazda RX-7")
    rid = race.create_race("Sunset Dash", "easy", 2000)

    ok = race.enter_racer(rid, mid, cid)
    assert ok, "Valid entry should succeed"
    details = race.get_race_details(rid)
    assert len(details["participants"]) == 1
    assert details["participants"][0]["driver_id"] == mid
    assert not crew.is_available(mid), "Driver should be marked busy after entry"

def test_enter_non_driver(reg, crew, inv, race):
    mid = reg.register_member("Ivan", "mechanic")
    crew.assign_role(mid, "mechanic")
    cid = inv.add_car("Ford Mustang")
    rid = race.create_race("Bay Run", "medium", 3000)

    ok = race.enter_racer(rid, mid, cid)
    assert not ok, "Non-driver should not be allowed to race"

def test_enter_unregistered_driver(inv, race):
    cid = inv.add_car("Dodge Viper")
    rid = race.create_race("Ghost Race", "easy", 1000)
    ok  = race.enter_racer(rid, "CREW-999", cid)
    assert not ok, "Unknown driver should be rejected"

def test_enter_damaged_car(reg, crew, inv, race):
    mid = reg.register_member("Jack", "driver")
    crew.assign_role(mid, "driver")
    cid = inv.add_car("Subaru Impreza")
    inv.update_car_condition(cid, 85)     # 100 - 85 = 15% remaining
    rid = race.create_race("Wreck Rally", "medium", 2000)
    ok  = race.enter_racer(rid, mid, cid)
    assert not ok, "Car at 15% should be unavailable"

def test_driver_double_entry(reg, crew, inv, race):
    mid  = reg.register_member("Kim", "driver")
    crew.assign_role(mid, "driver")
    cid  = inv.add_car("Mitsubishi Eclipse")
    cid2 = inv.add_car("Pontiac Firebird")
    rid  = race.create_race("Double Trouble", "easy", 1500)

    race.enter_racer(rid, mid, cid)
    # driver is now busy; try to enter again
    ok = race.enter_racer(rid, mid, cid2)
    assert not ok, "Same driver should not enter twice"