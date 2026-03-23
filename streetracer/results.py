"""
Results Module
--------------
Processes completed races: awards prize money, applies wear/tear,
levels up the winning driver, and maintains a leaderboard.

Depends on: RaceManagementModule, CrewManagementModule, InventoryModule
"""

from raceManagement import RaceManagementModule
from crewManagement import CrewManagementModule
from inventory import InventoryModule

# damage applied to each participating car per race (percentage points)
RACE_DAMAGE: dict[str, int] = {
    "easy":    10,
    "medium":  20,
    "hard":    30,
    "extreme": 45,
}

# skill XP awarded to the winning driver
WIN_SKILL_DELTA = 5


class ResultsModule:

    def __init__(self, race_mod: RaceManagementModule,
                 crew_mod: CrewManagementModule,
                 inventory_mod: InventoryModule):
        self.race_mod      = race_mod
        self.crew_mod      = crew_mod
        self.inventory_mod = inventory_mod
        # {race_id: {"winner": driver_id, "payout": int, "finishers": [driver_id, ...]}}
        self.completed_races: dict = {}

    def process_race_results(self, race_id: str,
                             winning_driver_id: str,
                             finisher_order: list[str] | None = None) -> bool:
        """
        Processes race outcome:
          1. Validates race and winner
          2. Awards prize money to inventory
          3. Applies difficulty-scaled damage to all participant cars
          4. Levels up the winning driver's reflexes
          5. Marks race Completed; releases drivers and cars
        `finisher_order` is optional (list of driver_ids in finishing position).
        """
        print(f"\n--- Processing Results: {race_id} ---")

        race_details = self.race_mod.get_race_details(race_id)
        if not race_details:
            print(f"FAIL [Results]: Race {race_id} does not exist.")
            return False
        if race_id in self.completed_races:
            print(f"FAIL [Results]: Race {race_id} has already been processed.")
            return False
        if race_details["status"] not in ("Open", "In Progress"):
            print(f"FAIL [Results]: Race is in state '{race_details['status']}', "
                  "cannot process.")
            return False

        participants = race_details["participants"]
        if not participants:
            print(f"FAIL [Results]: No participants recorded for {race_id}.")
            return False

        # validate winner is a participant
        participant_driver_ids = [p["driver_id"] for p in participants]
        if winning_driver_id not in participant_driver_ids:
            print(f"FAIL [Results]: Driver {winning_driver_id} "
                  f"was not a participant in {race_id}.")
            return False

        # award prize money
        prize = race_details["prize_money"]
        self.inventory_mod.update_cash(
            prize, reason=f"Prize: {race_details['name']}")

        # apply car damage (difficulty-scaled)
        difficulty  = race_details["difficulty"]
        damage      = RACE_DAMAGE.get(difficulty, 15)
        print(f"DAMAGE: Applying {damage}% wear to all participant cars "
              f"(difficulty: {difficulty})...")
        for participant in participants:
            self.inventory_mod.update_car_condition(participant["car_id"], damage)

        # level up winner
        winner_skills = self.crew_mod.get_member_skills(winning_driver_id)
        if winner_skills:
            self.crew_mod.increment_skill(winning_driver_id, "reflexes", WIN_SKILL_DELTA)
            self.crew_mod.record_race_win(winning_driver_id)
            winner_name = self.crew_mod.registration_mod.get_member(
                winning_driver_id)["name"]
            print(f"WIN XP: {winner_name} +{WIN_SKILL_DELTA} reflexes.")

        # release all drivers and cars back to available
        for participant in participants:
            self.crew_mod.set_availability(participant["driver_id"], True)
            self.inventory_mod.set_car_race_status(participant["car_id"], False)

        # mark completed
        race_details["status"] = "Completed"
        self.completed_races[race_id] = {
            "winner":        winning_driver_id,
            "payout":        prize,
            "finishers":     finisher_order or participant_driver_ids,
            "difficulty":    difficulty,
        }

        print(f"SUCCESS [Results]: '{race_details['name']}' concluded. "
              f"Winner: {winning_driver_id}")
        return True

    def get_leaderboard(self) -> list[tuple[str, int]]:
        """Returns (driver_id, win_count) sorted descending."""
        wins: dict[str, int] = {}
        for race in self.completed_races.values():
            w = race["winner"]
            wins[w] = wins.get(w, 0) + 1
        return sorted(wins.items(), key=lambda x: x[1], reverse=True)

    def print_leaderboard(self) -> None:
        board = self.get_leaderboard()
        print("\n=== Leaderboard ===")
        if not board:
            print("  No races completed yet.")
        for rank, (driver_id, wins) in enumerate(board, 1):
            member = self.crew_mod.registration_mod.get_member(driver_id)
            name = member["name"] if member else driver_id
            print(f"  #{rank}  {driver_id} | {name:<20} | {wins} win(s)")
        print()

    def get_race_result(self, race_id: str) -> dict | None:
        return self.completed_races.get(race_id)
