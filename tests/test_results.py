import pytest

@pytest.mark.parametrize("inv", [0], indirect=True)
def test_process_valid_race_result(reg, crew, inv, race, res):
    mid = reg.register_member("Lena", "driver")
    crew.assign_role(mid, "driver")
    cid = inv.add_car("Nissan 350Z")
    rid = race.create_race("Night Race", "easy", 3000)
    race.enter_racer(rid, mid, cid)

    ok = res.process_race_results(rid, mid)
    assert ok, "Result processing should succeed"
    assert inv.cash_balance == 3000, f"Expected 3000, got {inv.cash_balance}"
    assert inv.get_car(cid)["condition"] == 90, "Easy race deals 10 damage"
    assert crew.is_available(mid), "Driver should be freed after race"

def test_winner_not_in_race(reg, crew, inv, race, res):
    mid1 = reg.register_member("Marco", "driver")
    mid2 = reg.register_member("Nina", "driver")
    crew.assign_role(mid1, "driver")
    crew.assign_role(mid2, "driver")
    cid = inv.add_car("Toyota AE86")
    rid = race.create_race("Solo Run", "easy", 1000)
    race.enter_racer(rid, mid1, cid)

    ok = res.process_race_results(rid, mid2)
    assert not ok, "Non-participant cannot be declared winner"

def test_process_same_race_twice(reg, crew, inv, race, res):
    mid = reg.register_member("Omar", "driver")
    crew.assign_role(mid, "driver")
    cid = inv.add_car("Nissan Silvia")
    rid = race.create_race("One Shot", "easy", 500)
    race.enter_racer(rid, mid, cid)
    res.process_race_results(rid, mid)

    ok = res.process_race_results(rid, mid)
    assert not ok, "Race should not be processed twice"
    assert inv.cash_balance == 10500, "Cash should not be doubled (10000 start + 500 prize)"

def test_leaderboard_ordering(reg, crew, inv, race, res):
    d1 = reg.register_member("Petra", "driver")
    d2 = reg.register_member("Quinn", "driver")
    crew.assign_role(d1, "driver")
    crew.assign_role(d2, "driver")

    for i in range(3):
        cid1 = inv.add_car(f"Car A{i}")
        cid2 = inv.add_car(f"Car B{i}")
        rid  = race.create_race(f"Race {i}", "easy", 100)
        winner = d1 if i < 2 else d2
        loser  = d2 if i < 2 else d1
        wcar   = cid1 if i < 2 else cid2
        lcar   = cid2 if i < 2 else cid1
        race.enter_racer(rid, winner, wcar)
        race.enter_racer(rid, loser,  lcar)
        res.process_race_results(rid, winner)

    board = res.get_leaderboard()
    assert board[0][0] == d1, "d1 should be #1 (2 wins)"
    assert board[0][1] == 2
    assert board[1][0] == d2
    assert board[1][1] == 1

def test_winner_skill_increment(reg, crew, inv, race, res):
    mid = reg.register_member("Rosa", "driver")
    crew.assign_role(mid, "driver")
    cid = inv.add_car("Alfa Romeo")
    rid = race.create_race("Skill Test", "medium", 1000)
    race.enter_racer(rid, mid, cid)
    res.process_race_results(rid, mid)
    skills = crew.get_member_skills(mid)["skills"]
    assert skills["reflexes"] == 5, f"Expected 5, got {skills['reflexes']}"