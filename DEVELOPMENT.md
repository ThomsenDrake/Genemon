# Genemon Development Guide

## For Future Iterations

This guide is for future development iterations of Genemon. It explains the codebase structure, design decisions, and how to extend the project.

## Architecture Overview

### Modular Design

Genemon uses a modular architecture with clear separation of concerns:

```
genemon/
├── core/       - Game engine, creatures, save system
├── creatures/  - Generation and type system
├── sprites/    - Sprite generation
├── battle/     - Combat mechanics
├── world/      - Maps and NPCs
└── ui/         - Display and interface
```

Each module is self-contained and can be modified independently.

### Key Design Principles

1. **Immutable Species**: `CreatureSpecies` is the template, `Creature` is the instance
2. **Seed-based Generation**: All randomness uses a seed for reproducibility
3. **No External Dependencies**: Pure Python stdlib only
4. **JSON Serialization**: All game state is JSON-serializable
5. **Terminal-First**: UI designed for terminal, but extensible to GUI

## Core Data Models

### Creature Hierarchy

```python
CreatureSpecies (Template)
  ├── id, name, types
  ├── base_stats (CreatureStats)
  ├── moves (List[Move])
  ├── flavor_text
  ├── evolution_level, evolves_into
  └── sprite_data

Creature (Instance)
  ├── species (reference to CreatureSpecies)
  ├── level, exp
  ├── current_hp, max_hp
  ├── nickname
  └── calculated stats (attack, defense, etc.)

Team
  └── creatures (List[Creature], max 6)
```

### Game State

```python
GameState
  ├── seed (for generation)
  ├── species_dict (all 151 CreatureSpecies)
  ├── player_team (Team)
  ├── storage (List[Creature])
  ├── current_location, player_x, player_y
  ├── pokedex_seen, pokedex_caught
  ├── badges, flags, defeated_trainers
  └── items (Dict[str, int])
```

## How to Extend

### Adding New Creatures

The generator creates 151 by default. To change this:

1. Edit `creatures/generator.py`
2. Modify `generate_all_creatures()` to generate more/fewer
3. Update documentation references to "151"

### Adding New Types

1. Edit `creatures/types.py`
2. Add type name to `TYPES` list
3. Add effectiveness relationships in `TYPE_EFFECTIVENESS`
4. Add color in `TYPE_COLORS` (for sprites)

Example:
```python
TYPES.append("Dragon")

TYPE_EFFECTIVENESS["Dragon"] = {
    "Dragon": 2.0,  # Super effective vs Dragon
    "Metal": 0.5,   # Not very effective vs Metal
}

TYPE_COLORS["Dragon"] = [
    Color(100, 50, 200),  # Primary
    Color(150, 100, 255), # Secondary
    Color(80, 30, 180)    # Dark
]
```

### Adding New Moves

Moves are generated procedurally. To add custom moves:

1. Edit `creatures/generator.py`
2. Create custom moves in `_generate_creature()`:

```python
custom_move = Move(
    name="Dragon Breath",
    type="Dragon",
    power=60,
    accuracy=100,
    pp=20,
    max_pp=20,
    description="Unleashes dragon fire"
)
species.moves.append(custom_move)
```

### Adding New Locations

1. Edit `world/map.py`
2. Add location in `World._create_world()`:

```python
new_town = LocationBuilder.create_town(
    "town_new",
    "New Town Name",
    width=20,
    height=20
)
self.locations[new_town.id] = new_town
```

3. Set up connections:

```python
existing_town.connections["town_new"] = (10, 0)
new_town.connections["town_existing"] = (10, 19)
```

### Adding New NPCs

1. Edit `world/npc.py`
2. Add NPC in `NPCRegistry._create_npcs()`:

```python
new_npc = NPC(
    id="npc_unique_id",
    name="NPC Name",
    location_id="town_new",
    x=10,
    y=10,
    sprite="N",
    is_trainer=True,  # If trainer
    dialogues=[
        Dialogue("Hello, traveler!"),
        Dialogue("Let's battle!", "before_battle")
    ]
)
self.npcs[new_npc.id] = new_npc
```

### Adding Items

Currently items are basic. To extend:

1. Create `genemon/core/items.py`:

```python
@dataclass
class Item:
    id: str
    name: str
    description: str
    type: str  # "healing", "capture", "status"
    effect: dict

class ItemSystem:
    def use_item(self, item: Item, target: Creature):
        if item.type == "healing":
            target.heal(item.effect["amount"])
        # etc.
```

2. Update `GameState` to track items
3. Add item menu in `core/game.py`

### Adding Status Effects

1. Create `battle/status.py`:

```python
class StatusEffect(Enum):
    BURN = "burn"
    POISON = "poison"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    FROZEN = "frozen"

@dataclass
class Creature:
    # ... existing fields
    status: Optional[StatusEffect] = None
```

2. Update `battle/engine.py` to apply status effects each turn
3. Add status-inflicting moves

### Improving Sprite Generation

Current sprites are abstract. To improve:

1. Edit `sprites/generator.py`
2. Add more archetypes:

```python
def _draw_dragon_creature(self, sprite, palette, size):
    # Draw dragon-specific features
    # - Long neck
    # - Wings
    # - Tail
    # - Horns
    pass
```

3. Add more detail layers (eyes, patterns, accessories)
4. Implement better color blending

### Adding PNG Export

To export sprites as PNG files:

```python
from PIL import Image  # Would need to add dependency

def export_sprite_to_png(sprite_data: List[List[str]], filename: str):
    height = len(sprite_data)
    width = len(sprite_data[0])

    img = Image.new('RGB', (width, height))
    pixels = []

    for row in sprite_data:
        for pixel in row:
            if pixel == "transparent":
                pixels.append((0, 0, 0, 0))  # Transparent
            else:
                # Convert hex to RGB
                rgb = tuple(int(pixel.lstrip('#')[i:i+2], 16)
                           for i in (0, 2, 4))
                pixels.append(rgb)

    img.putdata(pixels)
    img.save(filename)
```

### Adding GUI

To create a GUI version:

1. Use pygame or tkinter
2. Create `genemon/ui/gui.py`
3. Render sprites from sprite_data
4. Replace Display class calls with GUI rendering

Basic pygame structure:
```python
import pygame

class GameGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))

    def render_sprite(self, sprite_data):
        for y, row in enumerate(sprite_data):
            for x, color in enumerate(row):
                if color != "transparent":
                    rgb = self.hex_to_rgb(color)
                    pygame.draw.rect(
                        self.screen,
                        rgb,
                        (x * 4, y * 4, 4, 4)  # 4x scale
                    )
```

## Testing

### Running Tests

```bash
python3 test_genemon.py
```

### Adding Tests

Add to `test_genemon.py`:

```python
def test_new_feature():
    """Test description."""
    print("Testing new feature...")

    try:
        # Test code here
        assert condition, "Error message"
        print("  ✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

# Add to main():
tests.append(test_new_feature)
```

### Manual Testing Checklist

- [ ] New game creation works
- [ ] Save/load preserves state
- [ ] Battles execute correctly
- [ ] Movement and collisions work
- [ ] NPCs interact properly
- [ ] Pokedex updates correctly
- [ ] Capture mechanics function
- [ ] Evolution triggers at correct level
- [ ] Type effectiveness calculates right

## Common Tasks

### Adjusting Difficulty

**Starter Stats**:
```python
# In creatures/generator.py
def _generate_starter_trio(self):
    # Change power_level from "starter" to "intermediate"
    creature = self._generate_creature(
        creature_id=i,
        power_level="intermediate",  # Was "starter"
        stage=1,
        types=types
    )
```

**Capture Rates**:
```python
# In battle/engine.py
def try_capture(self, ball_strength: float = 1.0):
    # Increase/decrease catch_rate formula
    catch_rate = (hp_factor * 50 + 10) * ball_strength
    # Change 50 to higher number = easier catches
```

**Wild Encounter Rates**:
```python
# In world/map.py
row.append(Tile(
    TileType.GRASS,
    True,
    can_encounter=True,
    encounter_rate=0.15  # Lower = fewer encounters
))
```

### Balancing Types

Edit `creatures/types.py`:

```python
TYPE_EFFECTIVENESS = {
    "Flame": {
        "Leaf": 2.0,   # Super effective
        "Aqua": 0.5,   # Not very effective
        # Adjust these multipliers for balance
    }
}
```

### Adding More Locations

1. Create location with `LocationBuilder`
2. Add to `World._create_world()`
3. Set up connections with existing locations
4. Add NPCs for that location
5. Update QUICKSTART.md with new location

### Improving Name Generation

Edit `creatures/generator.py`:

```python
# Add more name components
PREFIXES = [
    # Add more prefixes
    "Drak", "Syl", "Nyx", "Zor", ...
]

# Or use a different algorithm
def _generate_name(self):
    # Custom name generation logic
    syllables = [
        self.rng.choice(["dra", "syl", "nyx"]),
        self.rng.choice(["ko", "ra", "ven"]),
        self.rng.choice(["x", "on", "is"])
    ]
    return "".join(syllables).capitalize()
```

## Debugging

### Common Issues

**Import Errors**:
- Check all `__init__.py` files exist
- Verify Python path includes project root

**Save/Load Errors**:
- Check JSON structure is valid
- Ensure all classes have `to_dict()` and `from_dict()`
- Verify sprite_data is serializable

**Battle Bugs**:
- Check damage formula doesn't divide by zero
- Ensure HP doesn't go negative
- Verify type effectiveness lookup doesn't KeyError

**Generation Issues**:
- Check random seed is set correctly
- Verify all 151 creatures are created
- Ensure no duplicate names

### Debug Mode

Add to `main.py`:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In code:
logger.debug(f"Creature: {creature.name}, HP: {creature.current_hp}")
```

## Performance Optimization

### Sprite Generation

Currently generates all sprites at game start. To optimize:

1. Generate sprites on-demand (lazy loading)
2. Cache generated sprites
3. Use simpler sprite generation for common creatures

```python
class SpriteCache:
    def __init__(self):
        self.cache = {}

    def get_sprite(self, creature_id, types, archetype):
        if creature_id not in self.cache:
            gen = SpriteGenerator()
            self.cache[creature_id] = gen.generate_creature_sprites(
                creature_id, types, archetype
            )
        return self.cache[creature_id]
```

### Save File Size

To reduce save file size:

1. Don't save sprite_data in every save (regenerate on load)
2. Compress JSON with gzip
3. Use more compact data format

```python
import gzip
import json

def save_compressed(data, filename):
    with gzip.open(filename, 'wt') as f:
        json.dump(data, f)

def load_compressed(filename):
    with gzip.open(filename, 'rt') as f:
        return json.load(f)
```

## Code Style

### Conventions

- **Classes**: PascalCase (`CreatureSpecies`, `BattleEngine`)
- **Functions**: snake_case (`generate_creature`, `execute_turn`)
- **Constants**: UPPER_SNAKE_CASE (`TYPE_EFFECTIVENESS`, `TYPES`)
- **Private methods**: `_method_name` (single underscore)

### Documentation

- All public classes need docstrings
- All public methods need docstrings
- Use type hints where helpful
- Add inline comments for complex logic

Example:
```python
def calculate_damage(
    self,
    attacker: Creature,
    defender: Creature,
    move: Move
) -> int:
    """
    Calculate damage for an attack.

    Args:
        attacker: The attacking creature
        defender: The defending creature
        move: The move being used

    Returns:
        Damage amount (minimum 1)
    """
    # Implementation
```

## Iteration Best Practices

### Before Making Changes

1. Read existing code thoroughly
2. Understand the architecture
3. Check if feature already exists
4. Plan changes before coding

### While Coding

1. Make incremental changes
2. Test frequently
3. Keep related changes together
4. Document as you go

### After Changes

1. Run test suite
2. Update CHANGELOG.md
3. Update relevant documentation
4. Test game end-to-end
5. Check for regressions

### Refactoring

When refactoring existing code:

1. Identify code smells (duplication, long methods, etc.)
2. Refactor one thing at a time
3. Maintain backward compatibility if possible
4. Update tests after refactoring

### Removing Code

Don't be afraid to delete:
- Unused functions/classes
- Commented-out code
- Obsolete features
- Redundant code

Document deletions in CHANGELOG.md.

## Version Control

### Commit Messages

Good commit messages:
```
Add dragon type to type system
Implement item usage in battles
Fix crash when capturing fainted creature
Refactor sprite generation for better performance
```

Bad commit messages:
```
updates
fix
changes
wip
```

### What to Commit

✅ DO commit:
- Source code changes
- Documentation updates
- Configuration files
- Test files

❌ DON'T commit:
- Save files (`saves/*.json`)
- Generated sprites (if saved to disk)
- Python cache (`__pycache__`, `*.pyc`)
- IDE files (`.vscode`, `.idea`)

## Resources

### Understanding the Codebase

1. Start with `main.py` - entry point
2. Read `core/game.py` - game loop
3. Explore `creatures/generator.py` - creature creation
4. Study `battle/engine.py` - combat mechanics

### Key Algorithms

**Damage Calculation** (`battle/engine.py:_calculate_damage`):
- Based on Generation 1 Pokemon formula
- Includes type effectiveness and STAB

**Stat Calculation** (`core/creature.py:_calculate_stats`):
- Simplified stat formula
- Scales with level

**Sprite Generation** (`sprites/generator.py`):
- Procedural drawing algorithms
- Archetype-based rendering

### External References

- Pokemon Damage Calculation: https://bulbapedia.bulbagarden.net/wiki/Damage
- Procedural Generation: https://www.redblobgames.com/
- Game Dev Patterns: https://gameprogrammingpatterns.com/

## Future Roadmap

### Short-term (Next 1-3 Iterations)
- Item system implementation
- Move PP tracking and restoration
- Better NPC trainer teams
- More locations and NPCs

### Mid-term (4-10 Iterations)
- Status effects
- Weather system
- Breeding mechanics
- Mini-games
- Better sprite rendering

### Long-term (10+ Iterations)
- GUI version
- Multiplayer features
- Sound and music
- More creature archetypes (500+?)
- Online features

---

**Happy coding!** 🚀

This is an evolving project. Each iteration should make it better while maintaining the core vision: a unique, procedurally-generated monster-collecting RPG experience.
