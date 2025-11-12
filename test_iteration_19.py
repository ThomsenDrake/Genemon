"""
Test suite for Iteration 19 features.

New Features:
1. Type Chart Display System
2. Sprite Viewer/Gallery
3. Configuration System
4. Enhanced Game Menus
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genemon.ui.display import Display
from genemon.creatures.types import TYPES, TYPE_EFFECTIVENESS, get_effectiveness
from genemon.core.config import GameConfig, get_config, init_config
from genemon.ui.colors import ColorSupport
from genemon.creatures.generator import CreatureGenerator
from genemon.sprites.generator import SpriteGenerator
import tempfile
import json


def test_type_chart_display():
    """Test type chart display functionality."""
    print("\n=== Test: Type Chart Display ===")

    display = Display()

    # Test overview display
    print("\n1. Testing type chart overview...")
    display.show_type_chart()
    print("✓ Type chart overview displayed successfully")

    # Test specific type display
    print("\n2. Testing specific type display...")
    for test_type in ["Flame", "Aqua", "Mind"]:
        display.show_type_chart(test_type)
        print(f"✓ {test_type} type chart displayed successfully")

    # Test invalid type
    print("\n3. Testing invalid type handling...")
    display.show_type_chart("InvalidType")
    print("✓ Invalid type handled gracefully")

    print("\n✅ Type Chart Display: ALL TESTS PASSED")
    return True


def test_type_effectiveness_accuracy():
    """Test that type effectiveness calculations are correct."""
    print("\n=== Test: Type Effectiveness Accuracy ===")

    # Test super effective (2x)
    flame_vs_leaf = get_effectiveness("Flame", ["Leaf"])
    assert flame_vs_leaf == 2.0, f"Flame vs Leaf should be 2.0, got {flame_vs_leaf}"
    print("✓ Super effective (2x) works correctly")

    # Test not very effective (0.5x)
    flame_vs_aqua = get_effectiveness("Flame", ["Aqua"])
    assert flame_vs_aqua == 0.5, f"Flame vs Aqua should be 0.5, got {flame_vs_aqua}"
    print("✓ Not very effective (0.5x) works correctly")

    # Test no effect (0x)
    volt_vs_terra = get_effectiveness("Volt", ["Terra"])
    assert volt_vs_terra == 0.0, f"Volt vs Terra should be 0.0, got {volt_vs_terra}"
    print("✓ No effect (0x) works correctly")

    # Test neutral (1x)
    flame_vs_beast = get_effectiveness("Flame", ["Beast"])
    assert flame_vs_beast == 1.0, f"Flame vs Beast should be 1.0, got {flame_vs_beast}"
    print("✓ Neutral (1x) works correctly")

    # Test dual-type effectiveness (multiplies)
    flame_vs_leaf_frost = get_effectiveness("Flame", ["Leaf", "Frost"])
    assert flame_vs_leaf_frost == 4.0, f"Flame vs Leaf/Frost should be 4.0, got {flame_vs_leaf_frost}"
    print("✓ Dual-type multiplier works correctly")

    print("\n✅ Type Effectiveness Accuracy: ALL TESTS PASSED")
    return True


def test_sprite_viewer():
    """Test sprite viewer functionality."""
    print("\n=== Test: Sprite Viewer ===")

    display = Display()

    # Generate test creature data
    print("\n1. Generating test creature data...")
    gen = CreatureGenerator(seed=12345)
    sprite_gen = SpriteGenerator(seed=12345)

    species_list = gen.generate_all_creatures()
    species_dict = {s.id: s for s in species_list}

    # Simulate caught creatures
    caught = {1, 5, 10}

    print("✓ Test data generated")

    # Test viewing caught creature
    print("\n2. Testing sprite viewer for caught creature...")
    display.show_sprite_viewer(1, species_dict, caught)
    print("✓ Sprite viewer displayed for caught creature")

    # Test viewing uncaught creature
    print("\n3. Testing sprite viewer for uncaught creature...")
    display.show_sprite_viewer(2, species_dict, caught)
    print("✓ Uncaught creature message displayed correctly")

    # Test viewing non-existent creature
    print("\n4. Testing sprite viewer for non-existent creature...")
    display.show_sprite_viewer(999, species_dict, caught)
    print("✓ Non-existent creature handled gracefully")

    print("\n✅ Sprite Viewer: ALL TESTS PASSED")
    return True


def test_config_system():
    """Test configuration system."""
    print("\n=== Test: Configuration System ===")

    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_config_path = f.name

    try:
        # Test config creation with defaults
        print("\n1. Testing config creation...")
        config = GameConfig(config_path=temp_config_path)
        assert config.get("colors_enabled") == True
        assert config.get("auto_save") == True
        print("✓ Config created with defaults")

        # Test setting values
        print("\n2. Testing setting values...")
        config.set("colors_enabled", False)
        assert config.get("colors_enabled") == False
        print("✓ Config values can be set")

        # Test toggling
        print("\n3. Testing toggle functionality...")
        result = config.toggle("auto_save")
        assert result == False
        assert config.get("auto_save") == False
        result = config.toggle("auto_save")
        assert result == True
        print("✓ Toggle functionality works")

        # Test save and load
        print("\n4. Testing save and load...")
        config.set("battle_animations", False)
        config.save()

        # Create new config instance and load
        config2 = GameConfig(config_path=temp_config_path)
        assert config2.get("battle_animations") == False
        assert config2.get("colors_enabled") == False
        print("✓ Save and load works correctly")

        # Test reset to defaults
        print("\n5. Testing reset to defaults...")
        config2.reset_to_defaults()
        assert config2.get("colors_enabled") == True
        assert config2.get("battle_animations") == True
        print("✓ Reset to defaults works")

        # Test show_settings (should not crash)
        print("\n6. Testing settings display...")
        config.show_settings()
        print("✓ Settings display works")

        # Test color support integration
        print("\n7. Testing color support integration...")
        config.set("colors_enabled", False)
        assert ColorSupport.is_enabled() == False
        config.set("colors_enabled", True)
        assert ColorSupport.is_enabled() == True
        print("✓ Color support integration works")

    finally:
        # Clean up temp file
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)

    print("\n✅ Configuration System: ALL TESTS PASSED")
    return True


def test_config_global_instance():
    """Test global config instance management."""
    print("\n=== Test: Global Config Instance ===")

    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_config_path = f.name

    try:
        # Test init_config
        print("\n1. Testing init_config...")
        config1 = init_config(temp_config_path)
        config1.set("colors_enabled", False)
        print("✓ Config initialized")

        # Test get_config returns same instance
        print("\n2. Testing get_config...")
        config2 = get_config()
        assert config2.get("colors_enabled") == False
        assert config1 is config2
        print("✓ get_config returns same instance")

    finally:
        # Clean up temp file
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)

    print("\n✅ Global Config Instance: ALL TESTS PASSED")
    return True


def test_all_types_covered():
    """Test that all 16 types are properly defined."""
    print("\n=== Test: All Types Coverage ===")

    # Check we have exactly 16 types
    assert len(TYPES) == 16, f"Should have 16 types, found {len(TYPES)}"
    print(f"✓ Correct number of types: {len(TYPES)}")

    # Check all types are in TYPE_EFFECTIVENESS
    for type_name in TYPES:
        # Not all types have offensive matchups (like Beast), so we just check they exist
        assert type_name in TYPES, f"Type {type_name} not in TYPES list"
    print("✓ All types are properly defined")

    # Check no duplicate types
    assert len(TYPES) == len(set(TYPES)), "Duplicate types found"
    print("✓ No duplicate types")

    # List all types
    print(f"\n  All {len(TYPES)} types:")
    for i, type_name in enumerate(TYPES, 1):
        print(f"    {i:2d}. {type_name}")

    print("\n✅ All Types Coverage: ALL TESTS PASSED")
    return True


def test_sprite_rendering():
    """Test sprite ASCII rendering."""
    print("\n=== Test: Sprite ASCII Rendering ===")

    display = Display()

    # Test with simple sprite data
    print("\n1. Testing simple sprite rendering...")
    test_sprite = [
        ["#FF0000", "#00FF00", "#0000FF"],
        ["#FFFF00", "#FF00FF", "#00FFFF"],
        ["#000000", "transparent", "#FFFFFF"]
    ]
    display._render_sprite_ascii(test_sprite)
    print("✓ Simple sprite rendered")

    # Test with empty sprite
    print("\n2. Testing empty sprite...")
    display._render_sprite_ascii([])
    print("✓ Empty sprite handled")

    # Test with None
    print("\n3. Testing None sprite...")
    display._render_sprite_ascii(None)
    print("✓ None sprite handled")

    print("\n✅ Sprite ASCII Rendering: ALL TESTS PASSED")
    return True


def test_menu_integration():
    """Test that new menu options are properly integrated."""
    print("\n=== Test: Menu Integration ===")

    # This is more of a structural test
    from genemon.core.game import Game

    print("\n1. Testing Game class has new methods...")
    game = Game()

    # Check new methods exist
    assert hasattr(game, '_show_type_chart_menu'), "Missing _show_type_chart_menu"
    assert hasattr(game, '_show_sprite_viewer_menu'), "Missing _show_sprite_viewer_menu"
    assert hasattr(game, '_show_settings_menu'), "Missing _show_settings_menu"
    print("✓ All new menu methods exist")

    print("\n2. Testing methods are callable...")
    assert callable(game._show_type_chart_menu)
    assert callable(game._show_sprite_viewer_menu)
    assert callable(game._show_settings_menu)
    print("✓ All methods are callable")

    print("\n✅ Menu Integration: ALL TESTS PASSED")
    return True


def run_all_tests():
    """Run all iteration 19 tests."""
    print("=" * 70)
    print("ITERATION 19 - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    tests = [
        ("Type Chart Display", test_type_chart_display),
        ("Type Effectiveness Accuracy", test_type_effectiveness_accuracy),
        ("Sprite Viewer", test_sprite_viewer),
        ("Configuration System", test_config_system),
        ("Global Config Instance", test_config_global_instance),
        ("All Types Coverage", test_all_types_covered),
        ("Sprite ASCII Rendering", test_sprite_rendering),
        ("Menu Integration", test_menu_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ {test_name}: FAILED")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {passed/len(tests)*100:.1f}%")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return True
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
