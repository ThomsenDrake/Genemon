# Genemon - Python Monster Collector RPG

A Python-based monster-collecting RPG where **each new save file generates 151 completely unique creatures** with procedural stats, moves, types, and pixel art sprites.

## Features

### Procedural Creature Generation
- **151 unique creatures per save file** - Each new game generates a completely fresh roster
- **Procedural sprites** - Actual pixel art (56x56 front, 56x56 back, 16x16 mini) generated algorithmically
- **Custom type system** - 16 unique types (Flame, Aqua, Leaf, Volt, etc.) with full effectiveness chart
- **Balanced stats** - Creatures have HP, Attack, Defense, Special, and Speed stats
- **Unique moves** - Each creature has 4-6 moves with varying power, accuracy, and PP
- **Evolution chains** - Some creatures evolve at specific levels

### Gameplay Systems
- **Turn-based battles** - Classic RPG combat with type effectiveness
- **Wild encounters** - Random battles in grass areas
- **Trainer battles** - Fight NPCs throughout the world
- **Capture system** - Catch wild creatures with capture balls
- **Experience & leveling** - Creatures gain EXP and level up
- **Team management** - Build a team of up to 6 creatures

### World & NPCs
- **Authored world map** - Fixed towns, routes, and caves to explore
- **NPCs** - Professors, trainers, healers, and shopkeepers
- **Multiple locations** - Towns, routes, caves with unique layouts
- **Pokedex** - Track creatures you've seen and caught

### Save System
- **Multiple save files** - Create different games with unique creature rosters
- **Export/Import** - Share creature rosters between saves
- **Persistent progress** - Save your journey at any time

## Installation

### Requirements
- Python 3.8 or higher
- No external dependencies required (uses only Python standard library)

### Setup
```bash
# Clone or download the repository
cd loop

# Run the game
python main.py
```

## Quick Start

1. **Run the game**: `python main.py`
2. **Create a new game**: Choose "New Game" from the main menu
3. **Enter your name** and **save file name**
4. **Choose your starter** creature (Flame, Aqua, or Leaf type)
5. **Start your adventure!**

## How to Play

### Controls
- **Main Menu**: Number keys to select options
- **Movement**: W/A/S/D for up/left/down/right
- **Battles**: Number keys to select actions and moves

### Game Flow
1. Start in **Newbark Village** with your chosen starter
2. Explore **routes** and encounter **wild creatures**
3. Battle **trainers** and earn experience
4. **Capture** wild creatures to build your team
5. Collect **badges** from gym leaders (coming soon!)
6. Complete your **Pokedex** by seeing and catching all 151 creatures

### Battle System
- Choose from **Attack**, **Switch**, **Capture** (wild), or **Run** (wild)
- Type effectiveness matters - use super effective moves!
- STAB bonus (Same Type Attack Bonus) gives 1.5x damage
- Creatures gain EXP when they defeat opponents
- Level up to increase stats and potentially evolve

## Architecture

### Module Structure
```
genemon/
├── core/               # Core game systems
│   ├── creature.py     # Creature, Move, Team, Stats classes
│   ├── game.py         # Main game loop and engine
│   └── save_system.py  # Save/load functionality
├── creatures/          # Creature generation
│   ├── generator.py    # Procedural creature generation
│   └── types.py        # Type system and effectiveness
├── sprites/            # Sprite generation
│   └── generator.py    # Pixel art sprite generation
├── battle/             # Battle system
│   └── engine.py       # Turn-based battle mechanics
├── world/              # World and NPCs
│   ├── map.py          # Locations and tiles
│   └── npc.py          # NPCs and dialogue
└── ui/                 # User interface
    └── display.py      # Terminal-based display
```

### Key Classes

#### Creature System
- **CreatureSpecies**: Template for a creature type (one of the 151)
- **Creature**: Individual creature instance with level, HP, etc.
- **Move**: Attack with type, power, accuracy, PP
- **Team**: Collection of up to 6 creatures

#### Generation
- **CreatureGenerator**: Generates all 151 species for a save
- **SpriteGenerator**: Creates pixel art sprites for each species

#### Battle
- **Battle**: Handles turn-based combat logic
- **BattleAction**: ATTACK, SWITCH, ITEM, RUN
- **BattleResult**: ONGOING, PLAYER_WIN, OPPONENT_WIN, etc.

#### World
- **World**: Container for all locations
- **Location**: A map area (town, route, cave)
- **Tile**: Individual map tile with terrain type
- **NPC**: Non-player character with dialogue

## Creature Generation Details

### Name Generation
- Pronounceable names using prefix + middle + suffix system
- Examples: "Flarax", "Aquoton", "Thornicus"
- Guaranteed unique within a save file

### Stat Generation
Power levels determine stat ranges:
- **Basic**: 30-50 base stats (early game)
- **Starter**: 40-60 base stats
- **Intermediate**: 50-75 base stats
- **Advanced**: 65-95 base stats
- **Legendary**: 90-120 base stats

### Type Distribution
- 60% single-type, 40% dual-type
- Types: Flame, Aqua, Leaf, Volt, Frost, Terra, Gale, Toxin, Mind, Spirit, Beast, Brawl, Insect, Metal, Mystic, Shadow

### Sprite Generation
Each creature gets three sprites:
- **Front sprite** (56x56): Shown during battles (opponent view)
- **Back sprite** (56x56): Shown during battles (your creature)
- **Mini sprite** (16x16): Shown on overworld (future feature)

Sprites are procedurally generated as 2D arrays of hex colors based on:
- Type (determines color palette)
- Archetype (bird, fish, quadruped, serpent, etc.)
- Random seed (ensures reproducibility)

## Save File Format

Save files are stored as JSON in the `saves/` directory:

```json
{
  "version": "0.1.0",
  "save_name": "mysave",
  "player_name": "Ash",
  "seed": 123456,
  "species": { ... },  // All 151 generated creatures
  "player_team": { ... },
  "pokedex_seen": [1, 2, 3],
  "pokedex_caught": [1],
  ...
}
```

## Future Enhancements

- Gym battles and badge system
- Item system (potions, status healers, etc.)
- Shop system
- More complex AI for trainer battles
- Move PP management and restoration
- Status effects (poison, paralysis, etc.)
- Weather effects
- Graphical sprites display (PNG export)
- Sound effects and music
- Multiplayer battles

## Development

### Code Style
- Python 3.8+ features
- Type hints where helpful
- Docstrings for all classes and public methods
- Modular architecture for easy extension

### Testing
Currently manual testing. Future: Add pytest suite.

### Contributing
This is an autonomous AI project, but suggestions are welcome!

## Credits

**Developed by**: Claude Code (Anthropic's autonomous coding agent)

**Inspired by**: Classic monster-collecting RPGs (without copying any copyrighted content)

## License

To be determined.

---

**Generated and maintained by Claude Code**
