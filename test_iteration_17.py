"""
Test suite for Iteration 17: Revival Items, PNG Export, Color Terminal
"""

import sys
import random

# Set up test environment
def setup_test():
    """Initialize test environment."""
    random.seed(12345)  # Consistent results
    return True

def test_revival_items():
    """Test revival item system (Revive and Max Revive)."""
    print("Testing revival item system...")

    from genemon.core.items import ITEMS, ItemType, ItemEffect
    from genemon.creatures.generator import CreatureGenerator
    from genemon.core.creature import Creature

    # Generate test creature
    gen = CreatureGenerator(seed="test_revival")
    species_list = gen.generate_all_creatures()
    species = species_list[0]

    # Create a creature and make it faint
    creature = Creature(species=species, level=10)
    original_max_hp = creature.max_hp
    creature.current_hp = 0  # Faint the creature

    # Test 1: Verify creature is fainted
    assert creature.is_fainted(), "Creature should be fainted"
    print("  ✓ Creature is properly fainted")

    # Test 2: Get Revive item
    revive = ITEMS['revive']
    assert revive.item_type == ItemType.REVIVAL, "Revive should be REVIVAL type"
    assert revive.effect == ItemEffect.REVIVE_HP, "Revive should have REVIVE_HP effect"
    print("  ✓ Revive item exists with correct type and effect")

    # Test 3: Verify Revive can be used on fainted creature
    can_use, message = revive.can_use_on(creature, in_battle=False)
    assert can_use, f"Revive should be usable on fainted creature: {message}"
    print("  ✓ Revive can be used on fainted creature")

    # Test 4: Use Revive and check HP restoration
    result_message = revive.use(creature)
    assert not creature.is_fainted(), "Creature should no longer be fainted"
    expected_hp = int(original_max_hp * 0.5)
    assert creature.current_hp == expected_hp, f"Should restore 50% HP: expected {expected_hp}, got {creature.current_hp}"
    print(f"  ✓ Revive restored 50% HP ({creature.current_hp}/{original_max_hp})")
    print(f"    Message: {result_message}")

    # Test 5: Verify Revive cannot be used on non-fainted creature
    can_use, message = revive.can_use_on(creature, in_battle=False)
    assert not can_use, "Revive should not be usable on non-fainted creature"
    assert "not fainted" in message.lower(), "Error message should mention creature is not fainted"
    print("  ✓ Revive cannot be used on non-fainted creature")

    # Test 6: Test Max Revive
    creature.current_hp = 0  # Faint again
    max_revive = ITEMS['max_revive']
    assert max_revive.item_type == ItemType.REVIVAL, "Max Revive should be REVIVAL type"
    assert max_revive.effect == ItemEffect.REVIVE_HP_FULL, "Max Revive should have REVIVE_HP_FULL effect"
    print("  ✓ Max Revive item exists with correct type and effect")

    # Test 7: Use Max Revive and verify full HP restoration
    result_message = max_revive.use(creature)
    assert not creature.is_fainted(), "Creature should no longer be fainted"
    assert creature.current_hp == original_max_hp, f"Should restore full HP: expected {original_max_hp}, got {creature.current_hp}"
    print(f"  ✓ Max Revive restored full HP ({creature.current_hp}/{original_max_hp})")
    print(f"    Message: {result_message}")

    # Test 8: Verify healing items cannot be used on fainted creatures
    from genemon.core.items import ITEMS as ALL_ITEMS
    potion = ALL_ITEMS['potion']
    creature.current_hp = 0  # Faint once more
    can_use, message = potion.can_use_on(creature, in_battle=False)
    assert not can_use, "Potion should not be usable on fainted creature"
    assert "fainted" in message.lower(), "Error message should mention creature is fainted"
    print("  ✓ Healing items correctly cannot be used on fainted creatures")

    # Test 9: Test revival also cures status effects
    from genemon.core.creature import StatusEffect
    creature.current_hp = 1
    creature.status = StatusEffect.BURN  # Apply burn
    assert creature.has_status(), "Creature should have burn status"
    creature.current_hp = 0  # Faint with status

    revive.use(creature)
    assert not creature.has_status(), "Revival should cure status effects"
    assert creature.status == StatusEffect.NONE, "Status should be NONE after revival"
    print("  ✓ Revival cures status effects")

    print("✅ Revival item system - PASSED\n")
    return True


def test_revival_constants():
    """Test that revival constants are properly defined."""
    print("Testing revival constants...")

    from genemon.core.constants import REVIVE_HP_PERCENT, MAX_REVIVE_HP_FULL

    # Test 1: Revive HP percent
    assert REVIVE_HP_PERCENT == 0.5, f"REVIVE_HP_PERCENT should be 0.5, got {REVIVE_HP_PERCENT}"
    print(f"  ✓ REVIVE_HP_PERCENT = {REVIVE_HP_PERCENT} (50%)")

    # Test 2: Max Revive full HP flag
    assert MAX_REVIVE_HP_FULL == True, f"MAX_REVIVE_HP_FULL should be True"
    print(f"  ✓ MAX_REVIVE_HP_FULL = {MAX_REVIVE_HP_FULL}")

    print("✅ Revival constants - PASSED\n")
    return True


def test_revival_item_prices():
    """Test that revival items have reasonable prices."""
    print("Testing revival item prices...")

    from genemon.core.items import ITEMS

    revive = ITEMS['revive']
    max_revive = ITEMS['max_revive']

    # Test 1: Revive price
    assert revive.price > 0, "Revive should have a price"
    assert revive.price == 800, f"Revive price should be 800, got {revive.price}"
    print(f"  ✓ Revive price: {revive.price}")

    # Test 2: Max Revive price should be higher
    assert max_revive.price > revive.price, "Max Revive should cost more than Revive"
    assert max_revive.price == 2000, f"Max Revive price should be 2000, got {max_revive.price}"
    print(f"  ✓ Max Revive price: {max_revive.price}")

    # Test 3: Descriptions
    assert "50%" in revive.description or "50" in revive.description, "Revive description should mention 50%"
    assert "full" in max_revive.description.lower(), "Max Revive description should mention full HP"
    print(f"  ✓ Revive description: {revive.description}")
    print(f"  ✓ Max Revive description: {max_revive.description}")

    print("✅ Revival item prices - PASSED\n")
    return True


def test_revival_in_battle():
    """Test that revival items work correctly in battle context."""
    print("Testing revival items in battle...")

    from genemon.core.items import ITEMS
    from genemon.creatures.generator import CreatureGenerator
    from genemon.core.creature import Creature, Team

    # Generate test creatures
    gen = CreatureGenerator(seed="test_battle_revival")
    species_list = gen.generate_all_creatures()

    # Create team with fainted creature
    creature1 = Creature(species=species_list[0], level=10)
    creature2 = Creature(species=species_list[1], level=10)
    creature1.current_hp = 0  # Faint first creature

    team = Team(creatures=[creature1, creature2])

    # Test 1: Revive can be used in battle
    revive = ITEMS['revive']
    can_use, message = revive.can_use_on(creature1, in_battle=True)
    assert can_use, f"Revive should be usable in battle: {message}"
    print("  ✓ Revive can be used in battle")

    # Test 2: Use revive in battle context
    result = revive.use(creature1)
    assert not creature1.is_fainted(), "Creature should be revived"
    assert creature1.current_hp > 0, "Creature should have HP after revival"
    print(f"  ✓ Creature revived in battle context: {result}")

    # Test 3: Max Revive in battle
    creature2.current_hp = 0  # Faint second creature
    max_revive = ITEMS['max_revive']
    can_use, message = max_revive.can_use_on(creature2, in_battle=True)
    assert can_use, f"Max Revive should be usable in battle: {message}"

    result = max_revive.use(creature2)
    assert creature2.current_hp == creature2.max_hp, "Max Revive should restore full HP"
    print(f"  ✓ Max Revive works in battle: {result}")

    print("✅ Revival in battle - PASSED\n")
    return True


def test_item_type_enum():
    """Test that ItemType enum includes REVIVAL."""
    print("Testing ItemType enum...")

    from genemon.core.items import ItemType

    # Test 1: REVIVAL type exists
    assert hasattr(ItemType, 'REVIVAL'), "ItemType should have REVIVAL"
    print("  ✓ ItemType.REVIVAL exists")

    # Test 2: REVIVAL value
    assert ItemType.REVIVAL.value == "revival", f"REVIVAL value should be 'revival', got '{ItemType.REVIVAL.value}'"
    print(f"  ✓ ItemType.REVIVAL.value = '{ItemType.REVIVAL.value}'")

    print("✅ ItemType enum - PASSED\n")
    return True


def test_item_effect_enum():
    """Test that ItemEffect enum includes revival effects."""
    print("Testing ItemEffect enum...")

    from genemon.core.items import ItemEffect

    # Test 1: REVIVE_HP exists
    assert hasattr(ItemEffect, 'REVIVE_HP'), "ItemEffect should have REVIVE_HP"
    print("  ✓ ItemEffect.REVIVE_HP exists")

    # Test 2: REVIVE_HP_FULL exists
    assert hasattr(ItemEffect, 'REVIVE_HP_FULL'), "ItemEffect should have REVIVE_HP_FULL"
    print("  ✓ ItemEffect.REVIVE_HP_FULL exists")

    # Test 3: Values
    assert ItemEffect.REVIVE_HP.value == "revive_hp", f"REVIVE_HP value incorrect"
    assert ItemEffect.REVIVE_HP_FULL.value == "revive_hp_full", f"REVIVE_HP_FULL value incorrect"
    print(f"  ✓ ItemEffect.REVIVE_HP.value = '{ItemEffect.REVIVE_HP.value}'")
    print(f"  ✓ ItemEffect.REVIVE_HP_FULL.value = '{ItemEffect.REVIVE_HP_FULL.value}'")

    print("✅ ItemEffect enum - PASSED\n")
    return True


def test_png_export():
    """Test PNG sprite export functionality."""
    print("Testing PNG sprite export...")

    import os
    import tempfile
    from genemon.sprites.generator import SpriteGenerator, Color

    # Test 1: Check export methods exist
    assert hasattr(SpriteGenerator, 'export_sprite_to_png'), "export_sprite_to_png method should exist"
    assert hasattr(SpriteGenerator, 'export_creature_sprites_to_png'), "export_creature_sprites_to_png method should exist"
    print("  ✓ PNG export methods exist")

    # Test 2: Create a simple test sprite
    test_sprite = [
        [Color(255, 0, 0), Color(0, 255, 0)],
        [Color(0, 0, 255), Color(255, 255, 0)]
    ]

    # Test 3: Export to temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_sprite.png")
        SpriteGenerator.export_sprite_to_png(test_sprite, test_file)

        # Verify file was created
        assert os.path.exists(test_file), f"PNG file should be created at {test_file}"
        print(f"  ✓ PNG file created: {test_file}")

        # Verify file has content
        file_size = os.path.getsize(test_file)
        assert file_size > 0, "PNG file should have content"
        print(f"  ✓ PNG file size: {file_size} bytes")

        # Verify PNG signature (first 8 bytes)
        with open(test_file, 'rb') as f:
            signature = f.read(8)
            expected_signature = b'\x89PNG\r\n\x1a\n'
            assert signature == expected_signature, f"PNG signature should match: got {signature.hex()}"
        print("  ✓ PNG file has valid signature")

    # Test 4: Test scaling
    with tempfile.TemporaryDirectory() as tmpdir:
        scaled_file = os.path.join(tmpdir, "scaled_sprite.png")
        SpriteGenerator.export_sprite_to_png(test_sprite, scaled_file, scale=2)

        assert os.path.exists(scaled_file), "Scaled PNG file should be created"
        scaled_size = os.path.getsize(scaled_file)
        print(f"  ✓ Scaled PNG created (scale=2): {scaled_size} bytes")

    # Test 5: Test full creature sprite export
    from genemon.creatures.generator import CreatureGenerator

    gen = CreatureGenerator(seed="test_png_export")
    species_list = gen.generate_all_creatures()
    species = species_list[0]

    sprite_gen = SpriteGenerator(seed=species.id)
    sprites_dict = sprite_gen.generate_creature_sprites(
        creature_id=species.id,
        types=species.types,
        archetype="quadruped"
    )
    # Convert hex arrays to Color arrays
    front = SpriteGenerator.hex_array_to_color_array(sprites_dict['front'])
    back = SpriteGenerator.hex_array_to_color_array(sprites_dict['back'])
    mini = SpriteGenerator.hex_array_to_color_array(sprites_dict['mini'])

    with tempfile.TemporaryDirectory() as tmpdir:
        SpriteGenerator.export_creature_sprites_to_png(
            front, back, mini,
            creature_name="test_creature",
            output_dir=tmpdir,
            scale=2
        )

        # Verify all three files were created
        front_file = os.path.join(tmpdir, "test_creature_front.png")
        back_file = os.path.join(tmpdir, "test_creature_back.png")
        mini_file = os.path.join(tmpdir, "test_creature_mini.png")

        assert os.path.exists(front_file), "Front sprite PNG should be created"
        assert os.path.exists(back_file), "Back sprite PNG should be created"
        assert os.path.exists(mini_file), "Mini sprite PNG should be created"

        front_size = os.path.getsize(front_file)
        back_size = os.path.getsize(back_file)
        mini_size = os.path.getsize(mini_file)

        print(f"  ✓ All three creature sprites exported:")
        print(f"    - Front: {front_size} bytes")
        print(f"    - Back: {back_size} bytes")
        print(f"    - Mini: {mini_size} bytes")

    print("✅ PNG export - PASSED\n")
    return True


def test_color_terminal():
    """Test terminal color support."""
    print("Testing terminal color support...")

    from genemon.ui.colors import (
        TerminalColors, ColorSupport, colored, colored_type,
        colored_hp, colored_status, bold, underline, TYPE_COLORS_ANSI
    )

    # Test 1: Check TerminalColors class exists
    assert hasattr(TerminalColors, 'RED'), "TerminalColors should have RED"
    assert hasattr(TerminalColors, 'GREEN'), "TerminalColors should have GREEN"
    assert hasattr(TerminalColors, 'RESET'), "TerminalColors should have RESET"
    print("  ✓ TerminalColors class has basic colors")

    # Test 2: Check color support detection
    is_supported = TerminalColors.is_supported()
    print(f"  ✓ Terminal color support detected: {is_supported}")

    # Test 3: Test colored function (works even if colors disabled)
    colored_text = colored("test", TerminalColors.RED)
    assert "test" in colored_text, "Colored text should contain original text"
    print(f"  ✓ colored() function works: '{colored_text}'")

    # Test 4: Test type coloring
    for type_name in ["Flame", "Aqua", "Leaf"]:
        result = colored_type(type_name)
        assert type_name in result, f"Colored type should contain type name: {type_name}"
    print("  ✓ Type coloring works for all types")

    # Test 5: Test HP coloring
    hp_high = colored_hp(80, 100)
    hp_mid = colored_hp(30, 100)
    hp_low = colored_hp(10, 100)
    assert "80/100" in hp_high, "HP string should contain values"
    assert "30/100" in hp_mid, "HP string should contain values"
    assert "10/100" in hp_low, "HP string should contain values"
    print("  ✓ HP coloring works for all levels")

    # Test 6: Test status coloring
    status_text = colored_status("burn")
    assert "BURN" in status_text.upper(), "Status should be uppercased"
    print("  ✓ Status coloring works")

    # Test 7: Test bold and underline
    bold_text = bold("test")
    underline_text = underline("test")
    assert "test" in bold_text, "Bold text should contain original"
    assert "test" in underline_text, "Underlined text should contain original"
    print("  ✓ Text formatting (bold, underline) works")

    # Test 8: Test ColorSupport enable/disable
    original_state = ColorSupport.is_enabled()
    ColorSupport.disable()
    assert not ColorSupport.is_enabled(), "ColorSupport should be disabled"
    ColorSupport.enable()
    assert ColorSupport.is_enabled(), "ColorSupport should be enabled"
    # Restore original state
    if original_state:
        ColorSupport.enable()
    else:
        ColorSupport.disable()
    print("  ✓ ColorSupport enable/disable works")

    # Test 9: Check all type colors defined
    expected_types = ["Flame", "Aqua", "Leaf", "Volt", "Frost", "Terra",
                     "Gale", "Toxin", "Mind", "Spirit", "Beast", "Brawl",
                     "Insect", "Metal", "Mystic", "Shadow"]
    for type_name in expected_types:
        assert type_name in TYPE_COLORS_ANSI, f"TYPE_COLORS_ANSI should have {type_name}"
    print(f"  ✓ All {len(expected_types)} type colors defined")

    print("✅ Color terminal support - PASSED\n")
    return True


def run_all_tests():
    """Run all iteration 17 tests."""
    print("=" * 60)
    print("GENEMON ITERATION 17 TEST SUITE")
    print("Testing Revival Items, PNG Export, Color Terminal")
    print("=" * 60 + "\n")

    tests = [
        ("ItemType enum", test_item_type_enum),
        ("ItemEffect enum", test_item_effect_enum),
        ("Revival constants", test_revival_constants),
        ("Revival item prices", test_revival_item_prices),
        ("Revival item system", test_revival_items),
        ("Revival in battle", test_revival_in_battle),
        ("PNG export", test_png_export),
        ("Color terminal", test_color_terminal),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ {test_name} - FAILED")
            print(f"   Error: {e}\n")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name} - ERROR")
            print(f"   Error: {type(e).__name__}: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {failed} test(s) failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    setup_test()
    success = run_all_tests()
    sys.exit(0 if success else 1)
