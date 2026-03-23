import pytest

@pytest.mark.parametrize("inv", [2000], indirect=True)
def test_full_season_scenario(reg, crew, inv, race, res, mis, rep, ws):
    drv = reg.register_member("Leo",  "driver")
    mec = reg.register_member("Maya", "mechanic")
    str_ = reg.register_member("Nico", "strategist")
    for mid, role in [(drv, "driver"), (mec, "mechanic"), (str_, "strategist")]:
        crew.assign_role(mid, role)
    crew.update_skill(drv, "reflexes", 40)
    crew.update_skill(mec, "repair_speed", 55)

    cid = inv.add_car("Dodge Charger")
    inv.add_part("Turbocharger", 3)
    inv.add_tool("Torque Wrench")
    assert inv.cash_balance == 2000

    msn = mis.create_mission("Intel Run", "surveillance",
                             {"driver": 1, "strategist": 1}, reward=3000)
    ok = mis.assign_and_execute_mission(msn, [drv, str_])
    assert ok and inv.cash_balance == 5000, f"After mission: {inv.cash_balance}"

    rid = race.create_race("City Circuit", "hard", 7000)
    race.enter_racer(rid, drv, cid)
    res.process_race_results(rid, drv)

    assert inv.cash_balance == 12_000, f"After race: {inv.cash_balance}"
    car_cond = inv.get_car(cid)["condition"]
    assert car_cond == 70, f"Hard race (30 dmg): expected 70%, got {car_cond}%"

    ok_repair = ws.repair_car(cid, mechanic_id=mec, target_condition=100)
    assert ok_repair
    repair_cost = 30 * 20
    assert inv.cash_balance == 12_000 - repair_cost, \
        f"After repair: {inv.cash_balance}"
    assert inv.get_car(cid)["condition"] == 100

    ws.install_upgrade(cid, "turbo_kit", mechanic_id=mec)
    rival_id = rep.add_rival("Neon Wolves", rival_rep=250)
    rep.challenge_rival(rival_id, player_won=True)
    assert rep.reputation > 0

    board = res.get_leaderboard()
    assert board[0][0] == drv and board[0][1] == 1

    print("\n  [Scenario Summary]")
    inv.summary()
    crew.summary()
    res.print_leaderboard()
    rep.summary()
    ws.summary()
