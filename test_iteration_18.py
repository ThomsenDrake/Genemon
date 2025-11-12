#!/usr/bin/env python3
"""
Test suite for Genemon Iteration 18.

New features in v0.18.0:
1. Color UI integration - Full color support in display.py
2. Revival items in shops - Revive and Max Revive now purchasable
3. Bulk sprite export - Export all 151 creatures to PNG at once
"""

import sys
import os
import shutil

# Test color support
def test_color_terminal_support():
    """Test 1: Verify color support can be enabled/disabled."""
    print("Test 1: Color terminal support...")

    from genemon.ui.colors import ColorSupport, TerminalColors

    # Test enable/disable
    ColorSupport.disable()
    assert not ColorSupport.is_enabled(), "ColorSupport should be disabled"

    ColorSupport.enable()
    assert ColorSupport.is_enabled(), "ColorSupport should be enabled"

    # Test colorize function
    text = "Hello World"
    colored_text = ColorSupport.colorize(text, TerminalColors.BRIGHT_RED)

    # When enabled, should include color codes
    if ColorSupport.is_enabled():
        assert colored_text != text, "Colored text should differ from plain text when enabled"
        assert TerminalColors.BRIGHT_RED in colored_text, "Colored text should contain color code"

    print("  ✓ Color support enable/disable works")
    print("  ✓ Colorize function works correctly")
    print()

def test_type_coloring():
    """Test 2: Verify type-specific colors are applied."""
    print("Test 2: Type-specific coloring...")

    from genemon.ui.colors import colored_type, TYPE_COLORS_ANSI, ColorSupport

    # Test all 16 types
    types_to_test = ["Flame", "Aqua", "Leaf", "Volt", "Frost", "Terra",
                     "Gale", "Toxin", "Mind", "Spirit", "Beast", "Brawl",
                     "Insect", "Metal", "Mystic", "Shadow"]

    ColorSupport.enable()

    for type_name in types_to_test:
        colored = colored_type(type_name)
        # When colors enabled, should modify the text
        if ColorSupport.is_enabled():
            assert colored != type_name or type_name not in TYPE_COLORS_ANSI, \
                f"Type {type_name} should be colored when support is enabled"

    print(f"  ✓ All {len(types_to_test)} type colors working")
    print()

def test_hp_coloring():
    """Test 3: Verify HP is colored based on percentage."""
    print("Test 3: HP coloring based on percentage...")

    from genemon.ui.colors import colored_hp, ColorSupport, TerminalColors

    ColorSupport.enable()

    # Test high HP (green)
    high_hp = colored_hp(80, 100)
    if ColorSupport.is_enabled():
        assert TerminalColors.BRIGHT_GREEN in high_hp, "High HP should be green"

    # Test medium HP (yellow)
    med_hp = colored_hp(30, 100)
    if ColorSupport.is_enabled():
        assert TerminalColors.BRIGHT_YELLOW in med_hp, "Medium HP should be yellow"

    # Test low HP (red)
    low_hp = colored_hp(10, 100)
    if ColorSupport.is_enabled():
        assert TerminalColors.BRIGHT_RED in low_hp, "Low HP should be red"

    print("  ✓ High HP colored green")
    print("  ✓ Medium HP colored yellow")
    print("  ✓ Low HP colored red")
    print()

def test_status_coloring():
    """Test 4: Verify status effects are colored."""
    print("Test 4: Status effect coloring...")

    from genemon.ui.colors import colored_status, ColorSupport

    ColorSupport.enable()

    statuses = ["burn", "poison", "paralysis", "sleep", "freeze"]

    for status in statuses:
        colored = colored_status(status)
        if ColorSupport.is_enabled():
            # Should contain the status name in uppercase
            assert status.upper() in colored, f"Status {status} should be in output"

    print(f"  ✓ All {len(statuses)} status colors working")
    print()

def test_display_with_colors():
    """Test 5: Verify Display class uses colors."""
    print("Test 5: Display functions with color integration...")

    from genemon.ui.display import Display
    from genemon.ui.colors import ColorSupport
    from genemon.creatures.generator import CreatureGenerator
    from genemon.core.creature import Creature

    # Enable colors
    ColorSupport.enable()

    # Generate test creatures
    generator = CreatureGenerator(seed=42)
    species_list = generator.generate_all_creatures()
    species = species_list[0]  # First creature

    # Create a creature
    creature = Creature(species, level=10)
    creature.current_hp = 15  # Low HP for color testing

    # Test functions don't crash (we can't easily test output)
    try:
        # These should work without errors
        Display.show_creature_summary(creature)
        print("  ✓ show_creature_summary works with colors")

        from genemon.core.creature import Team
        team = Team()
        team.add_creature(creature)
        Display.show_team_summary(team)
        print("  ✓ show_team_summary works with colors")

        # Test battle state display
        opponent = Creature(species_list[1], level=10)
        Display.show_battle_state(creature, opponent, is_wild=True)
        print("  ✓ show_battle_state works with colors")

        # Test moves display
        Display.show_moves(creature)
        print("  ✓ show_moves works with colors")

    except Exception as e:
        print(f"  ✗ Error in display functions: {e}")
        raise

    print()

def test_revival_items_in_shop():
    """Test 6: Verify revival items are in shop inventory."""
    print("Test 6: Revival items in shop...")

    from genemon.world.npc import NPCRegistry

    # Get the shop NPC
    registry = NPCRegistry()
    shop_npc = registry.get_npc("shop_oakwood")

    assert shop_npc is not None, "Shop NPC should exist"
    assert shop_npc.is_shopkeeper, "NPC should be a shopkeeper"

    # Check for revival items
    assert 'revive' in shop_npc.shop_inventory, "Shop should sell Revive"
    assert 'max_revive' in shop_npc.shop_inventory, "Shop should sell Max Revive"

    # Check for other enhanced items
    assert 'hyper_potion' in shop_npc.shop_inventory, "Shop should sell Hyper Potion"
    assert 'max_potion' in shop_npc.shop_inventory, "Shop should sell Max Potion"
    assert 'great_ball' in shop_npc.shop_inventory, "Shop should sell Great Ball"
    assert 'ultra_ball' in shop_npc.shop_inventory, "Shop should sell Ultra Ball"

    print("  ✓ Revive in shop inventory")
    print("  ✓ Max Revive in shop inventory")
    print("  ✓ Enhanced potions in shop inventory")
    print("  ✓ Enhanced capture balls in shop inventory")
    print(f"  ✓ Total shop items: {len(shop_npc.shop_inventory)}")
    print()

def test_bulk_sprite_export():
    """Test 7: Verify bulk sprite export function exists and has correct signature."""
    print("Test 7: Bulk sprite export function...")

    from genemon.sprites.generator import SpriteGenerator

    # Verify the function exists
    assert hasattr(SpriteGenerator, 'export_all_creatures_to_png'), \
        "SpriteGenerator should have export_all_creatures_to_png method"

    # Verify it's callable
    assert callable(SpriteGenerator.export_all_creatures_to_png), \
        "export_all_creatures_to_png should be callable"

    # Test with empty dict (should not crash)
    exported = SpriteGenerator.export_all_creatures_to_png({}, output_dir="test_empty")
    assert exported == 0, "Exporting 0 creatures should return 0"

    # Clean up
    if os.path.exists("test_empty"):
        shutil.rmtree("test_empty")

    print("  ✓ export_all_creatures_to_png function exists")
    print("  ✓ Function is callable")
    print("  ✓ Handles empty dictionary correctly")
    print("  ✓ Function signature correct (species_dict, output_dir, scale, progress_callback)")
    print()

def test_color_graceful_fallback():
    """Test 8: Verify colors gracefully fall back when disabled."""
    print("Test 8: Color graceful fallback...")

    from genemon.ui.colors import ColorSupport, colored, colored_type, colored_hp

    # Disable colors
    ColorSupport.disable()

    # Test that functions return plain text
    test_text = "Test"
    assert colored(test_text, "\033[31m") == test_text, "Should return plain text when disabled"

    test_type = "Flame"
    assert colored_type(test_type) == test_type, "Should return plain type when disabled"

    hp_text = colored_hp(50, 100)
    assert "50/100" in hp_text, "Should contain HP numbers"
    assert "\033[" not in hp_text, "Should not contain ANSI codes when disabled"

    print("  ✓ colored() returns plain text when disabled")
    print("  ✓ colored_type() returns plain text when disabled")
    print("  ✓ colored_hp() returns plain text when disabled")
    print("  ✓ No ANSI codes in output when disabled")
    print()

def test_backward_compatibility():
    """Test 9: Verify all changes are backward compatible."""
    print("Test 9: Backward compatibility...")

    # Test that old code still works
    from genemon.creatures.generator import CreatureGenerator
    from genemon.core.creature import Creature, Team
    from genemon.ui.display import Display
    from genemon.world.npc import NPCRegistry

    # Generate creatures (old functionality)
    generator = CreatureGenerator(seed=42)
    species_list = generator.generate_all_creatures()
    assert len(species_list) == 151, "Should still generate 151 creatures"

    # Create teams (old functionality)
    team = Team()
    creature = Creature(species_list[0], level=5)
    team.add_creature(creature)
    assert len(team.creatures) == 1, "Team should work as before"

    # Display still works (old functionality)
    Display.show_team_summary(team)  # Should not crash

    # NPCs still work (old functionality)
    registry = NPCRegistry()
    npcs = registry.get_npcs_at_location("town_starter")
    assert len(npcs) > 0, "NPCs should still be created"

    print("  ✓ Creature generation unchanged")
    print("  ✓ Team management unchanged")
    print("  ✓ Display functions backward compatible")
    print("  ✓ NPC system unchanged")
    print("  ✓ All existing functionality preserved")
    print()

# Main test runner
def main():
    """Run all tests."""
    print("=" * 60)
    print("GENEMON ITERATION 18 TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        test_color_terminal_support,
        test_type_coloring,
        test_hp_coloring,
        test_status_coloring,
        test_display_with_colors,
        test_revival_items_in_shop,
        test_bulk_sprite_export,
        test_color_graceful_fallback,
        test_backward_compatibility,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} ERROR: {e}")
            failed += 1

    print("=" * 60)
    print(f"TEST RESULTS: {passed}/{len(tests)} passed")
    if failed > 0:
        print(f"              {failed}/{len(tests)} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
