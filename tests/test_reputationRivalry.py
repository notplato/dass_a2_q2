def test_reputation_event_application(rep):
    rep.apply_reputation_event("race_win")
    assert rep.reputation == 25
    rep.apply_reputation_event("race_loss")
    assert rep.reputation == 15

def test_reputation_clamp(rep):
    rep.add_reputation(2000, "overflow test")
    assert rep.reputation == 1000
    rep.add_reputation(-5000, "underflow test")
    assert rep.reputation == 0

def test_rival_defeat_bonus(rep):
    rid = rep.add_rival("Shadow Syndicate", rival_rep=300)
    before = rep.reputation
    rep.challenge_rival(rid, player_won=True)
    assert rep.reputation > before, "Defeating rival should increase rep"

def test_difficulty_gate(rep):
    assert not rep.can_access_difficulty("extreme"), "Extreme locked at rep 0"
    rep.add_reputation(500, "grind")
    assert rep.can_access_difficulty("extreme"), "Extreme unlocked at rep 500"