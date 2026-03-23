def test_register_valid_member(reg):
    mid = reg.register_member("Alice", "driver")
    assert mid is not None,                         "Should return an ID"
    assert mid.startswith("CREW-"),                 "ID should start with CREW-"
    member = reg.get_member(mid)
    assert member is not None,                      "Member should be retrievable"
    assert member["name"]   == "Alice",             "Name mismatch"
    assert member["role"]   == "driver",            "Role mismatch"
    assert member["status"] == "Active",            "Status should be Active"

def test_register_duplicate_ids(reg):
    id1 = reg.register_member("Bob", "mechanic")
    id2 = reg.register_member("Bob", "mechanic")
    assert id1 != id2, "Duplicate names should still get unique IDs"

def test_register_invalid_role(reg):
    mid = reg.register_member("Eve", "pirate")
    assert mid is None, "Invalid role should return None"
    assert len(reg.list_all_members()) == 0, "Registry should remain empty"

def test_register_empty_name(reg):
    mid = reg.register_member("", "driver")
    assert mid is None, "Empty name should return None"

def test_deactivate_and_reactivate(reg):
    mid = reg.register_member("Carlos", "strategist")
    assert reg.is_active(mid)
    reg.deactivate_member(mid)
    assert not reg.is_active(mid), "Should be Inactive after deactivation"
    reg.reactivate_member(mid)
    assert reg.is_active(mid), "Should be Active after reactivation"
