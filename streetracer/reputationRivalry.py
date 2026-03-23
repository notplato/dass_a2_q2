"""
Reputation & Rivalry Module
-----------------------------------------------------
Tracks the team's overall reputation score and manages rival crews.

Depends on: nothing (can observe results module events).
"""


REPUTATION_THRESHOLDS = {
    "Unknown":   0,
    "Rookie":    100,
    "Known":     250,
    "Respected": 500,
    "Feared":    750,
    "Legend":    900,
}

REP_EVENTS = {
    "race_win":         25,
    "race_loss":        -10,
    "mission_complete": 15,
    "rival_defeat":     75,   # base; scaled by rival strength
    "car_destroyed":    -20,
    "mission_fail":     -5,
}


class ReputationRivalryModule:

    def __init__(self):
        self.reputation: int = 0
        self.rep_history: list[dict] = []   # audit trail

        # {rival_id: {"name": str, "rep": int, "defeated": bool}}
        self.rivals: dict = {}
        self.rival_counter: int = 1

    def apply_reputation_event(self, event_type: str,
                                description: str = "") -> int:
        """
        Applies a named reputation event.
        Returns the new reputation score.
        """
        delta = REP_EVENTS.get(event_type, 0)
        old   = self.reputation
        self.reputation = max(0, min(1000, self.reputation + delta))
        self.rep_history.append({
            "event":       event_type,
            "delta":       delta,
            "rep_after":   self.reputation,
            "description": description,
        })
        direction = f"+{delta}" if delta >= 0 else str(delta)
        print(f"REP [{direction}] '{event_type}': {old} → {self.reputation} "
              f"| Tier: {self.get_tier()}")
        return self.reputation

    def add_reputation(self, amount: int, reason: str = "") -> int:
        """Direct reputation addition (for custom events)."""
        old = self.reputation
        self.reputation = max(0, min(1000, self.reputation + amount))
        self.rep_history.append({
            "event":       "manual",
            "delta":       amount,
            "rep_after":   self.reputation,
            "description": reason,
        })
        direction = f"+{amount}" if amount >= 0 else str(amount)
        print(f"REP [{direction}] {reason}: {old} → {self.reputation} "
              f"| Tier: {self.get_tier()}")
        return self.reputation

    def get_tier(self) -> str:
        """Returns the current reputation tier name."""
        tier = "Unknown"
        for name, threshold in sorted(REPUTATION_THRESHOLDS.items(),
                                       key=lambda x: x[1]):
            if self.reputation >= threshold:
                tier = name
        return tier

    def can_access_difficulty(self, difficulty: str) -> bool:
        """
        Gate-checks whether the current reputation allows a given race difficulty.
        easy → 0, medium → 100, hard → 250, extreme → 500
        """
        req = {"easy": 0, "medium": 100, "hard": 250, "extreme": 500}
        return self.reputation >= req.get(difficulty.lower(), 0)

    def add_rival(self, name: str, rival_rep: int = 200) -> str:
        """Registers a rival crew."""
        if not name or not name.strip():
            print("FAIL [Reputation]: Rival name cannot be empty.")
            return ""
        rival_id = f"RIVAL-{self.rival_counter:03d}"
        self.rivals[rival_id] = {
            "name":     name.strip(),
            "rep":      max(0, rival_rep),
            "defeated": False,
        }
        self.rival_counter += 1
        print(f"RIVAL ADDED: '{name}' (ID: {rival_id}, Rep: {rival_rep})")
        return rival_id

    def challenge_rival(self, rival_id: str, player_won: bool) -> bool:
        """
        Resolves a challenge against a rival.
        Win → big rep bonus (scaled to rival strength).
        Loss → moderate rep penalty.
        """
        rival = self.rivals.get(rival_id)
        if not rival:
            print(f"FAIL [Reputation]: Rival {rival_id} not found.")
            return False
        if rival["defeated"]:
            print(f"INFO [Reputation]: '{rival['name']}' has already been defeated.")
            return False

        if player_won:
            bonus = max(REP_EVENTS["rival_defeat"],
                        int(rival["rep"] * 0.4))
            self.add_reputation(bonus, reason=f"Defeated rival '{rival['name']}'")
            rival["defeated"] = True
            print(f"VICTORY: Rival '{rival['name']}' has been eliminated!")
        else:
            penalty = REP_EVENTS["race_loss"]
            self.add_reputation(penalty, reason=f"Lost to rival '{rival['name']}'")
            print(f"DEFEAT: Lost challenge against '{rival['name']}'.")

        return True

    def get_status(self) -> dict:
        return {
            "reputation":      self.reputation,
            "tier":            self.get_tier(),
            "active_rivals":   sum(1 for r in self.rivals.values()
                                   if not r["defeated"]),
            "rivals_defeated": sum(1 for r in self.rivals.values()
                                   if r["defeated"]),
        }

    def summary(self) -> None:
        s = self.get_status()
        print(f"\n=== Reputation & Rivalry ===")
        print(f"  Score : {s['reputation']} / 1000  |  Tier: {s['tier']}")
        print(f"  Rivals: {s['active_rivals']} active, "
              f"{s['rivals_defeated']} defeated")
        if self.rivals:
            for rid, r in self.rivals.items():
                status = "DEFEATED" if r["defeated"] else "Active"
                print(f"    {rid} | {r['name']:<20} | Rep: {r['rep']} | {status}")
        print()
