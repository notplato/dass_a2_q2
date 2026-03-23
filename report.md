# StreetRace Manager — Project Report

**Key integration paths:**

| Integration Path | Triggered By |
|---|---|
| Registration → CrewManagement | `assign_role()` validates member exists and is active |
| CrewManagement → Race Management | `enter_racer()` checks driver role and availability |
| Inventory → Race Management | `enter_racer()` checks car condition and assignment status |
| Race Management → Results | `process_race_results()` reads race participants and prize |
| Results → Inventory | Prize money deposited via `update_cash()` |
| Results → CrewManagement | Winner's reflexes incremented via `increment_skill()` |
| CrewManagement → Mission Planning | `assign_and_execute_mission()` validates roles and availability |
| Inventory → Mission Planning | Parts consumed via `use_part()` |
| CrewManagement + Inventory → GarageWorkshop | Repair requires mechanic + cash |

---


### Reputation & Rivalry Module *(Additional #1)*

**File:** `reputationRivalry.py`

**Why this module was added:** In an underground street racing world, reputation is just as important as money.  A team that has won many races and defeated rival crews is feared and respected, which opens doors to higher-stakes races.  Without a reputation system the game has no progression — every race feels equivalent regardless of history.

**What it does:**

The Reputation & Rivalry Module maintains the team's reputation score (0–1000) and manages rival crews.  Reputation increases when the team wins races, completes missions, and defeats rivals.  It decreases on losses or when a car is destroyed.

**Reputation tiers:**

| Tier | Minimum Score |
|---|---|
| Unknown | 0 |
| Rookie | 100 |
| Known | 250 |
| Respected | 500 |
| Feared | 750 |
| Legend | 900 |

**Difficulty gating:** Higher-difficulty races require a minimum reputation score.

| Race Difficulty | Required Reputation |
|---|---|
| Easy | 0 |
| Medium | 100 |
| Hard | 250 |
| Extreme | 500 |

**Rival system:** Rival crews have their own reputation score.  Challenging a rival and winning grants a reputation bonus scaled to the rival's strength (40% of their rep, minimum 75).  Losing to a rival costs reputation.  Once defeated, a rival is permanently marked as such.

**Integration points:**

- Other modules call `apply_reputation_event("race_win")` or `apply_reputation_event("mission_complete")` after their own processing to update reputation.
- Race Management can optionally call `can_access_difficulty(difficulty)` to gate race creation by reputation.

**Key methods:**

| Method | Purpose |
|---|---|
| `apply_reputation_event(event_type)` | Applies a named reputation change |
| `add_reputation(amount, reason)` | Manual reputation adjustment |
| `get_tier()` | Returns current tier name |
| `can_access_difficulty(difficulty)` | Checks if rep unlocks this difficulty |
| `add_rival(name, rep)` | Registers a rival crew |
| `challenge_rival(rival_id, player_won)` | Resolves a rivalry challenge |
| `get_status()` | Returns rep score, tier, and rival counts |

---

### Garage Workshop Module *(Additional #2)*

**File:** `garageWorkshop.py`

**Why this module was added:** After every race, cars take damage.  Without a way to repair them, the fleet would eventually become entirely unraceable.  The workshop creates a meaningful resource-management loop: win prize money → pay a mechanic to repair → re-enter next race.  The upgrade system adds a longer-term progression goal.

**What it does:**

The Garage Workshop Module provides paid repair and upgrade services for cars in the Inventory.  All workshop operations require an available mechanic from Crew Management and sufficient cash in Inventory.

**Repair system:**

- Cost: `$20 per condition point restored`
- Requires: an available mechanic
- Side effect: mechanic gains +2 `repair_speed` skill per repair job
- Side effect: mechanic is marked busy during the repair, then freed

**Upgrade system — available upgrades:**

| Upgrade Key | Description | Required Part | Cash Cost | Bonus | Max Level |
|---|---|---|---|---|---|
| `turbo_kit` | Increases speed attribute | Turbocharger ×1 | $1,500 | +10 speed | 3 |
| `racing_tyres` | Improves handling | Racing Slicks ×4 | $800 | +8 handling | 2 |
| `roll_cage` | Increases durability (reduces race damage) | None | $1,200 | +5 durability | 2 |

Each car tracks its own upgrade levels and attribute values (speed, handling, durability — each starting at 50/100).

**Integration points:**

- Calls `inventory_mod.update_cash()` to charge repair/upgrade cost.
- Calls `inventory_mod.use_part()` to consume required parts.
- Calls `crew_mod.is_available()` and `crew_mod.set_availability()` to manage mechanic state.
- Calls `crew_mod.increment_skill()` to reward the mechanic.

**Key methods:**

| Method | Purpose |
|---|---|
| `repair_car(car_id, mechanic_id, target_condition)` | Repairs to target condition for a fee |
| `install_upgrade(car_id, upgrade_key, mechanic_id)` | Installs an upgrade on a car |
| `get_car_workshop_data(car_id)` | Returns upgrade levels and attribute values |
| `get_damage_reduction(car_id)` | Returns % damage reduction from durability upgrades |

---

## Integration Test Suite

The test suite contains **45 tests** across **10 phases**, all run from `test_integration.py`.  Every test is self-contained: it creates a fresh set of modules, runs a specific scenario, and asserts the expected outcome.

**Test result: 45 / 45 PASS**

---

### Phase 1 — Registration (T01–T05)

These tests cover the very first thing that must work: getting crew members into the system.  If registration is broken, nothing else can function.

---

#### T01 — Register valid member

**Scenario:** Register a new crew member with a valid name and role.

**Modules involved:** Registration

**Why this test is needed:** Every other module depends on crew members being registered.  This is the most fundamental operation in the system and must be verified first.

**Expected result:** A `CREW-001` ID is returned.  The registry contains the member with the correct name, role, and `Active` status.

**Actual result:** PASS — `register_member("Alice", "driver")` returned `CREW-001`.  `get_member("CREW-001")` returned the correct dict.

**Errors found:** None.

---

#### T02 — Register duplicate names → unique IDs

**Scenario:** Register two crew members with identical names.

**Modules involved:** Registration

**Why this test is needed:** The system must not confuse two different people just because they share a name.  IDs are the primary key, not names.

**Expected result:** Two distinct IDs (`CREW-001`, `CREW-002`) are issued.

**Actual result:** PASS — Both Bob entries received unique IDs.

**Errors found:** None.

---

#### T03 — Register with invalid role

**Scenario:** Attempt to register a member with `role = "pirate"`.

**Modules involved:** Registration

**Why this test is needed:** If invalid roles slip in at registration, every downstream check becomes unreliable.  Role validation must happen at the point of entry.

**Expected result:** `register_member` returns `None`.  Registry remains empty.

**Actual result:** PASS — Returned `None` with an error message.

**Errors found:** The original module did not validate roles at registration time (it only validated them during `assign_role`).  Added role validation to `register_member` in the enhancement pass.

---

#### T04 — Register with empty name

**Scenario:** Call `register_member("")` with an empty string for the name.

**Modules involved:** Registration

**Why this test is needed:** An empty name would make every log message and report unreadable.  Data integrity must be enforced at input.

**Expected result:** Returns `None`.

**Actual result:** PASS.

**Errors found:** None.

---

#### T05 — Deactivate and reactivate member

**Scenario:** Register a member, deactivate them, check status, reactivate, check status.

**Modules involved:** Registration

**Why this test is needed:** Crew members may retire or be suspended temporarily.  The system needs to handle this without deleting their history.  Other modules (Crew, Mission) also depend on the `is_active()` check.

**Expected result:** Status toggles between `Inactive` and `Active` correctly.

**Actual result:** PASS.

**Errors found:** None.

---

### Phase 2 — Crew Management (T06–T10)

These tests verify that roles and skills are managed correctly, and that the module respects the state coming from Registration.

---

#### T06 — Assign role to registered member

**Scenario:** Register a driver, then call `assign_role` with `"driver"`.

**Modules involved:** Registration → Crew Management

**Why this test is needed:** This is the core two-module integration that unlocks everything else.  The crew member must exist in Registration before Crew Management will accept them.

**Expected result:** Returns `True`.  `get_member_skills()` shows role = `"driver"` and all four driver skills initialised to 0.

**Actual result:** PASS — All four skills (`cornering`, `reflexes`, `throttle_control`, `stamina`) present and set to 0.

**Errors found:** None.

---

#### T07 — Assign role to unregistered member

**Scenario:** Call `assign_role("CREW-999", "driver")` without registering that ID.

**Modules involved:** Registration → Crew Management

**Why this test is needed:** Crew Management must ask Registration to verify the member before accepting them.  This tests that the integration guard-rail works.

**Expected result:** Returns `False`.  Crew details unchanged.

**Actual result:** PASS — Crew Management correctly looked up `CREW-999` in Registration and rejected it.

**Errors found:** None.

---

#### T08 — Assign role to inactive member

**Scenario:** Register a member, deactivate them via Registration, then try to assign a role.

**Modules involved:** Registration → Crew Management

**Why this test is needed:** An inactive (retired/suspended) member should not receive new role assignments.  This tests that Crew Management checks `is_active()` from Registration.

**Expected result:** Returns `False`.

**Actual result:** PASS.

**Errors found:** Original module only checked if the member existed, not whether they were active.  Added `is_active()` check to `assign_role`.

---

#### T09 — Update skill with clamping

**Scenario:** Set a driver's cornering to 75, then to 150 (should clamp to 100), then to -10 (should clamp to 0).

**Modules involved:** Crew Management

**Why this test is needed:** Skills outside `[0, 100]` would break game balance and comparisons.  Clamping must be enforced at the point of update.

**Expected result:** 75 → 100 (clamped) → 0 (clamped).

**Actual result:** PASS.

**Errors found:** None.

---

#### T10 — Update wrong-role skill

**Scenario:** Assign `"driver"` role to a member, then try to set their `engine_tuning` (a mechanic skill).

**Modules involved:** Crew Management

**Why this test is needed:** Drivers should not have mechanic skills.  Allowing this would corrupt the role system that Mission Planning and Race Management depend on.

**Expected result:** Returns `False`.  Skill unchanged.

**Actual result:** PASS — Error message correctly identified that `engine_tuning` is not a driver skill.

**Errors found:** None.

---

### Phase 3 — Inventory (T11–T14)

These tests verify the financial and physical resource layer that all other modules interact with.

---

#### T11 — Cash add/subtract + overdraft block

**Scenario:** Start with $1,000.  Add $500 (total $1,500).  Subtract $200 (total $1,300).  Attempt to subtract $2,000 (should fail).

**Modules involved:** Inventory

**Why this test is needed:** Prize money and repair costs both flow through `update_cash`.  An overdraft must be blocked, or the team could go into negative balance and continue operating, which breaks economic game balance.

**Expected result:** Balance = $1,300 after all operations; final balance unchanged on failed transaction.

**Actual result:** PASS.

**Errors found:** None.

---

#### T12 — Car condition tracking

**Scenario:** Add a car at 100%.  Apply 30 damage (should reach 70%).  Apply 200 damage (should clamp at 0%).

**Modules involved:** Inventory

**Why this test is needed:** Race Management filters available cars by condition.  If condition could go negative, filtering would break.

**Expected result:** 100% → 70% → 0% (clamped).

**Actual result:** PASS — Output printed "DESTROYED" when condition hit 0.

**Errors found:** None.

---

#### T13 — Available cars filter

**Scenario:** Add two cars.  Damage the second to 10%.  Call `get_available_cars()`.

**Modules involved:** Inventory

**Why this test is needed:** Race Management relies entirely on `get_available_cars()` to find valid cars.  If badly damaged cars appeared in this list, races could be entered with wrecks.

**Expected result:** Only the first car (100% condition) appears in the result.

**Actual result:** PASS.

**Errors found:** None.

---

#### T14 — Parts use and fail

**Scenario:** Add 2 Turbochargers.  Use 1 (should succeed, leaving 1).  Attempt to use 5 (should fail, leaving 1).

**Modules involved:** Inventory

**Why this test is needed:** Mission Planning consumes parts.  If `use_part` let the count go negative, the inventory would become corrupted.

**Expected result:** Count = 1 after successful use; count unchanged after failed use.

**Actual result:** PASS.

**Errors found:** None.

---

### Phase 4 — Race Management (T15–T20)

These tests validate the race entry gate — the most complex validation point in the system.

---

#### T15 — Create valid race

**Scenario:** Call `create_race("Midnight Run", "hard", 5000)`.

**Modules involved:** Race Management

**Why this test is needed:** Basic sanity check that race creation works before testing entry conditions.

**Expected result:** Returns a `RACE-001` ID.

**Actual result:** PASS.

**Errors found:** None.

---

#### T16 — Enter valid driver and car

**Scenario:** Register a driver, assign role, add a car, create a race, enter the driver.

**Modules involved:** Registration → Crew Management → Inventory → Race Management

**Why this test is needed:** This is the primary happy-path integration test.  It exercises four modules simultaneously and verifies data flows correctly between them.

**Expected result:** `enter_racer` returns `True`.  Participant appears in race details.  Driver is marked unavailable in Crew Management.

**Actual result:** PASS — Driver was locked (`available = False`) automatically upon entry.

**Errors found:** Original module did not lock the driver after entry.  Added `set_availability(driver_id, False)` call inside `enter_racer`.

---

#### T17 — Enter non-driver in race

**Scenario:** Register and assign role as `mechanic`.  Attempt to enter this member in a race.

**Modules involved:** Registration → Crew Management → Race Management

**Why this test is needed:** The spec explicitly states only drivers may race.  A mechanic mistakenly entered as a driver would undermine all role-based logic.

**Expected result:** Returns `False`.

**Actual result:** PASS — Error clearly states the member is a Mechanic, not a Driver.

**Errors found:** None.

---

#### T18 — Enter unregistered driver

**Scenario:** Attempt to enter `"CREW-999"` (never registered) into a race.

**Modules involved:** Crew Management → Race Management

**Why this test is needed:** The system must reject phantom IDs that were never created.

**Expected result:** Returns `False`.

**Actual result:** PASS.

**Errors found:** None.

---

#### T19 — Enter damaged car

**Scenario:** Add a car and damage it to 15% condition.  Attempt to enter it in a race.

**Modules involved:** Inventory → Race Management

**Why this test is needed:** A car at 15% is effectively a wreck.  Allowing it to race would be unrealistic and could destroy it entirely (causing it to fall to 0% after even easy race damage).

**Expected result:** Returns `False`.

**Actual result:** PASS — `get_available_cars()` correctly excluded the 15% car.

**Errors found:** None.

---

#### T20 — Prevent driver double-entry

**Scenario:** Enter driver Kim into Race 1 with Car 1.  Attempt to enter Kim into Race 1 again with Car 2.

**Modules involved:** Crew Management → Race Management

**Why this test is needed:** A driver physically cannot race two cars simultaneously.  The availability lock must prevent the second entry.

**Expected result:** Second entry returns `False`.

**Actual result:** PASS — After the first entry, Kim's `available` flag was `False`, causing the second entry to fail with "Driver is currently unavailable."

**Errors found:** None.

---

### Phase 5 — Results (T21–T25)

These tests cover the result-processing pipeline which is the biggest integration point in the system.

---

#### T21 — Process valid race result

**Scenario:** Full setup: register driver, assign role, add car, create race, enter driver, process result.

**Modules involved:** Registration → Crew Management → Inventory → Race Management → Results

**Why this test is needed:** This is the core end-to-end race loop.  It must be verified that prize money reaches Inventory, car takes correct damage, and driver is freed.

**Expected result:** Cash balance = $3,000 (prize).  Car condition = 90% (100% minus 10% easy damage).  Driver is available.

**Actual result:** PASS — All three post-conditions confirmed.

**Errors found:** Original module used a flat 15% damage figure regardless of difficulty.  Replaced with difficulty-scaled damage table.

---

#### T22 — Winner not in race → rejected

**Scenario:** Enter Driver Marco in a race.  Call `process_race_results` declaring Driver Nina (not entered) as the winner.

**Modules involved:** Race Management → Results

**Why this test is needed:** Declaring a non-participant as winner would award prize money to the wrong person and corrupt the leaderboard.

**Expected result:** Returns `False`.

**Actual result:** PASS.

**Errors found:** None.

---

#### T23 — Process same race twice → blocked

**Scenario:** Process a completed race a second time.

**Modules involved:** Race Management → Results → Inventory

**Why this test is needed:** Processing twice would double the prize money, which is a critical financial exploit.

**Expected result:** Second call returns `False`.  Cash balance unchanged from first processing.

**Actual result:** PASS — The `completed_races` dict check blocks the second call.

**Errors found:** During test writing, the starting cash was incorrectly asserted as `$500` (the prize) instead of `$10,500` (starting $10,000 + $500 prize).  Fixed the assertion to match the `_fresh_system(starting_cash=10_000)` default.

---

#### T24 — Leaderboard ordering

**Scenario:** Run three races.  Driver Petra wins races 1 and 2.  Driver Quinn wins race 3.

**Modules involved:** Results

**Why this test is needed:** The leaderboard must sort correctly.  If it doesn't, the displayed ranking would be wrong and useless.

**Expected result:** Petra first with 2 wins; Quinn second with 1 win.

**Actual result:** PASS.

**Errors found:** None.

---

#### T25 — Winner reflex skill increment

**Scenario:** Driver starts with 0 reflexes.  Win one race.

**Modules involved:** Crew Management → Results

**Why this test is needed:** Race wins should improve the driver's skills.  This tests the Results → Crew Management integration where `increment_skill` is called.

**Expected result:** reflexes = 5 after one win.

**Actual result:** PASS.

**Errors found:** None.

---

### Phase 6 — Mission Planning (T26–T30)

These tests validate the mission lifecycle from creation to completion.

---

#### T26 — Create and complete basic mission

**Scenario:** Register a driver, assign role, create a single-driver delivery mission, execute it.

**Modules involved:** Registration → Crew Management → Inventory → Mission Planning

**Why this test is needed:** Basic mission happy-path.  Verifies reward is deposited and mission is marked complete.

**Expected result:** `assign_and_execute_mission` returns `True`.  Cash = $2,000.  Mission status = "Completed".

**Actual result:** PASS.

**Errors found:** None.

---

#### T27 — Mission fails — missing roles

**Scenario:** Create a mission requiring 2 mechanics.  Assign only 1 mechanic.

**Modules involved:** Crew Management → Mission Planning

**Why this test is needed:** The role verification logic must count correctly.  This tests that `required_roles = {"mechanic": 2}` is not satisfied by 1 mechanic.

**Expected result:** Returns `False`.  Cash unchanged.

**Actual result:** PASS — Error message correctly states "Need 2 Mechanic(s), only 1 assigned."

**Errors found:** None.

---

#### T28 — Mission fails — missing parts

**Scenario:** Create a mission requiring 2 Turbochargers.  Stock only 1.

**Modules involved:** Inventory → Mission Planning

**Why this test is needed:** Part requirements must be checked before the mission starts, not after.  Consuming parts that don't exist would corrupt the inventory.

**Expected result:** Returns `False`.  Part count unchanged.

**Actual result:** PASS — Mission failed before any parts were consumed.

**Errors found:** Original module had no `required_parts` support at all.  Added the `required_parts` parameter and pre-flight part check.

---

#### T29 — Mission blocked by inactive member

**Scenario:** Register and assign role to a strategist, deactivate them, then try to use them in a mission.

**Modules involved:** Registration → Mission Planning

**Why this test is needed:** Inactive members must be excluded from all operations.  Without this check, a "retired" crew member could still be assigned missions.

**Expected result:** Returns `False`.

**Actual result:** PASS — Mission Planning correctly calls `registration_mod.is_active()` via Crew Management.

**Errors found:** Original module had no activity check.  Added active status verification.

---

#### T30 — Mission cannot be replayed

**Scenario:** Complete a mission successfully, then attempt to run it again with the same crew.

**Modules involved:** Mission Planning

**Why this test is needed:** Replaying a completed mission would allow infinite reward farming.

**Expected result:** Second call returns `False`.

**Actual result:** PASS.

**Errors found:** None.

---

### Phase 7 — Cross-Module Business Rules (T31–T36)

These are the most important tests.  They verify that the modules work correctly *together*, not just in isolation.

---

#### T31 — Register → race → result full flow

**Scenario:** Complete the full race workflow: register a driver with a skill pre-set, add a car, create a medium race, enter, process result, verify all three post-conditions.

**Modules involved:** All core modules (Registration, Crew, Inventory, Race, Results)

**Why this test is needed:** This is the primary integration scenario from the assignment specification.  Each step depends on the previous one succeeding.

**Expected result:** Cash = $9,000 ($1,000 starting + $8,000 prize).  Car condition = 80% (medium race = 20 damage).  Driver available.

**Actual result:** PASS — All three conditions confirmed.

**Errors found:** None.

---

#### T32 — Mechanic required after race damage

**Scenario:** Damage a car to 15% (below the 20% threshold).  Try to enter it in a race (should fail).  Use the Garage Workshop with a mechanic to repair it to 80%.  Try to enter again (should succeed).

**Modules involved:** Inventory → Race Management → Garage Workshop → Crew Management

**Why this test is needed:** This is one of the explicit integration scenarios from the spec: "If a car is damaged during a race, a mission requiring a mechanic must check for availability before proceeding."  The same principle applies to repairs.

**Expected result:** First entry fails.  Repair succeeds.  Second entry succeeds.

**Actual result:** PASS — The full repair-then-race cycle worked correctly.

**Errors found:** None.

---

#### T33 — Busy driver cannot race

**Scenario:** Manually set a driver's availability to `False` (simulating mid-mission), then attempt to enter them in a race.

**Modules involved:** Crew Management → Race Management

**Why this test is needed:** The same driver cannot simultaneously be on a mission and in a race.  The availability flag is the shared lock between these two modules.

**Expected result:** `enter_racer` returns `False`.

**Actual result:** PASS.

**Errors found:** Original module did not check availability at all — only checked role.  Added `is_available()` check to `enter_racer`.

---

#### T34 — Race result updates leaderboard and cash

**Scenario:** Complete a hard race with a $10,000 prize.  Verify cash and leaderboard simultaneously.

**Modules involved:** Race Management → Results → Inventory

**Why this test is needed:** These two side effects (money and leaderboard) happen in the same `process_race_results` call.  Both must be correct at the same time.

**Expected result:** Cash = $10,000.  Leaderboard shows winner with 1 win.

**Actual result:** PASS.

**Errors found:** None.

---

#### T35 — Multi-role mission requires all roles

**Scenario:** Create a mission needing 1 driver AND 1 strategist.  First attempt with only the driver (fails).  Second attempt with both (succeeds).

**Modules involved:** Registration → Crew Management → Mission Planning → Inventory

**Why this test is needed:** Multi-role missions test the role-counting logic.  Partial fulfilment must not be accepted.

**Expected result:** First attempt fails.  Second attempt succeeds with $4,000 deposited.

**Actual result:** PASS.

**Errors found:** None.

---

#### T36 — Car locked during race — no double booking

**Scenario:** Enter Driver Eli in Race 1 with the only available car.  Attempt to enter Driver Fay in Race 2 with the same car.

**Modules involved:** Inventory → Race Management

**Why this test is needed:** A single physical car cannot participate in two races at once.  The `set_car_race_status` lock must be set atomically with `enter_racer`.

**Expected result:** Second entry returns `False`.

**Actual result:** PASS — Inventory correctly reported car as unavailable after first entry.

**Errors found:** Original module had no car locking mechanism.  Added `set_car_race_status()` to Inventory and the lock/unlock calls to Race Management and Results.

---

### Phase 8 — Reputation & Rivalry (T37–T40)

---

#### T37 — Reputation event application

**Scenario:** Apply a `race_win` event (+25) then a `race_loss` event (-10).

**Modules involved:** Reputation & Rivalry

**Why this test is needed:** Verifies the event lookup table and arithmetic are correct.

**Expected result:** 0 → 25 → 15.

**Actual result:** PASS.

**Errors found:** None.

---

#### T38 — Reputation clamping

**Scenario:** Add 2,000 reputation (should cap at 1,000).  Subtract 5,000 (should floor at 0).

**Modules involved:** Reputation & Rivalry

**Why this test is needed:** Without clamping, reputation could exceed 1,000 or go negative, breaking tier comparisons.

**Expected result:** 0 → 1,000 (capped) → 0 (floored).

**Actual result:** PASS.

**Errors found:** None.

---

#### T39 — Rival defeat grants reputation bonus

**Scenario:** Add a rival with 300 reputation.  Challenge and win.

**Modules involved:** Reputation & Rivalry

**Why this test is needed:** Defeating rivals is a major reputation gain event.  The bonus must be calculated correctly (40% of rival's rep = 120).

**Expected result:** Reputation increases after the win.  Rival marked as defeated.

**Actual result:** PASS — +120 reputation awarded (40% of 300).

**Errors found:** None.

---

#### T40 — Difficulty gate by reputation

**Scenario:** Check `can_access_difficulty("extreme")` at 0 rep (should be False).  Add 500 rep.  Check again (should be True).

**Modules involved:** Reputation & Rivalry

**Why this test is needed:** The difficulty gate prevents new teams from immediately accessing extreme races.  This is a core progression mechanic.

**Expected result:** False at rep 0; True at rep 500.

**Actual result:** PASS.

**Errors found:** None.

---

### Phase 9 — Garage Workshop (T41–T44)

---

#### T41 — Basic car repair via workshop

**Scenario:** Add a mechanic, add a car, damage it to 60%, repair to 100%.

**Modules involved:** Inventory → Crew Management → Garage Workshop

**Why this test is needed:** Verifies the cost calculation, that cash is correctly deducted, and that the mechanic's skill improves.

**Expected result:** Car at 100%.  Cash reduced by $800 (40 points × $20).  Mechanic freed.

**Actual result:** PASS.

**Errors found:** None.

---

#### T42 — Repair blocked — insufficient funds

**Scenario:** Start with $100.  Damage car to 20% (needs 80 points repair = $1,600).  Attempt repair.

**Modules involved:** Inventory → Garage Workshop

**Why this test is needed:** Workshop must not proceed if the cash is insufficient, or the team ends up in debt.

**Expected result:** Returns `False`.  Car condition unchanged.

**Actual result:** PASS — `update_cash(-1600)` was blocked by the overdraft check, and the workshop correctly returned `False`.

**Errors found:** None.

---

#### T43 — Install upgrade

**Scenario:** Add a mechanic, add a car, stock 2 Turbochargers, install `turbo_kit`.

**Modules involved:** Inventory → Crew Management → Garage Workshop

**Why this test is needed:** Upgrade installation touches three modules simultaneously (cash, parts, crew availability).  All three must be updated correctly.

**Expected result:** Upgrade level = 1.  Speed attribute = 60 (50 base + 10 bonus).  Cash reduced by $1,500.  Turbocharger count reduced by 1.

**Actual result:** PASS.

**Errors found:** None.

---

#### T44 — Upgrade blocked at max level

**Scenario:** Install `racing_tyres` twice on the same car (max level = 2).  Attempt a third installation.

**Modules involved:** Garage Workshop

**Why this test is needed:** Max-level checks prevent unbounded stat inflation.

**Expected result:** Third call returns `False`.

**Actual result:** PASS.

**Errors found:** None.

---

### Phase 10 — Full End-to-End Scenario (T45)

---

#### T45 — Full season scenario

**Scenario:** A complete game-loop using all eight modules in sequence:
1. Register Leo (driver), Maya (mechanic), and Nico (strategist).
2. Set pre-existing skills for Leo and Maya.
3. Add a Dodge Charger to the garage; stock Turbochargers; acquire a Torque Wrench.
4. Create and complete a surveillance mission (Leo + Nico) → $3,000 reward.
5. Enter Leo in a hard race with the Charger → $7,000 prize; car drops to 70%.
6. Maya repairs the Charger to 100% for $600.
7. Maya installs a Turbo Kit on the Charger for $1,500.
8. Add rival "Neon Wolves" and defeat them → +100 rep.
9. Verify leaderboard, reputation, inventory, and garage state.

**Modules involved:** All eight modules

**Why this test is needed:** No individual test proves the modules work together across a realistic sequence.  This scenario shows that state changes made by one module are correctly observed by every subsequent module.

**Expected result:**

| Item | Expected |
|---|---|
| Cash after mission | $5,000 |
| Cash after race | $12,000 |
| Car condition after race | 70% |
| Cash after repair | $11,400 ($12,000 − $600) |
| Car condition after repair | 100% |
| Cash after upgrade | $9,900 ($11,400 − $1,500) |
| Car speed attribute | 60 (50 + 10 turbo bonus) |
| Reputation | > 0 (100 from rival defeat) |
| Leaderboard #1 | Leo, 1 win |

**Actual result:** PASS — All nine post-conditions confirmed.

**Errors found:** None.
