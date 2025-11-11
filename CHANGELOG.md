# Changelog

All notable changes to the Genemon project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2025-11-11 - Initial Release

### Added - Core Game Systems

#### Creature System
- **CreatureSpecies class** - Template for one of the 151 generated creatures
- **Creature class** - Individual creature instances with level, HP, exp, stats
- **Move class** - Attack moves with type, power, accuracy, PP
- **CreatureStats class** - Base stat structure (HP, Attack, Defense, Special, Speed)
- **Team class** - Collection of up to 6 creatures with management methods
- **Stat calculation system** - Generates actual stats from base stats and level
- **Experience and leveling** - Creatures gain EXP and level up with stat increases

#### Creature Generation System
- **CreatureGenerator class** - Procedurally generates all 151 creatures per save
- **Name generation** - Pronounceable names using prefix/middle/suffix system
- **Type assignment** - 60% single-type, 40% dual-type distribution
- **Stat generation** - Balanced stats based on power level (basic/starter/intermediate/advanced/legendary)
- **Move generation** - 4-6 unique moves per creature with appropriate power levels
- **Evolution chains** - Automatically sets up 2-stage and 3-stage evolution relationships
- **Starter trio** - Special generation for the three starter creatures (Flame/Aqua/Leaf)
- **Flavor text** - Unique description for each creature
- **151 unique creatures** - Complete roster generated from single seed

#### Type System
- **16 custom types** - Flame, Aqua, Leaf, Volt, Frost, Terra, Gale, Toxin, Mind, Spirit, Beast, Brawl, Insect, Metal, Mystic, Shadow
- **Full type effectiveness chart** - Super effective (2.0x), not very effective (0.5x), no effect (0.0x)
- **Type color mapping** - Visual colors for each type (for future UI enhancements)
- **Effectiveness calculator** - Handles single and dual-type matchups

#### Sprite Generation System
- **SpriteGenerator class** - Generates actual pixel art as 2D color arrays
- **Front sprites** - 56x56 pixel sprites for battle (opponent view)
- **Back sprites** - 56x56 pixel sprites for battle (player view)
- **Mini sprites** - 16x16 pixel sprites for overworld display
- **Type-based color palettes** - Each type has unique color schemes
- **Archetype system** - Different body types (bird, fish, quadruped, biped, serpent, blob)
- **Procedural drawing** - Algorithmic sprite generation with symmetry and details
- **Hex color output** - Sprites stored as 2D arrays of hex color strings
- **ASCII conversion** - Can display sprites as ASCII art in terminal
- **Reproducibility** - Same seed always generates same sprites

#### Battle System
- **Battle class** - Complete turn-based combat engine
- **BattleAction enum** - ATTACK, SWITCH, ITEM, RUN actions
- **BattleResult enum** - ONGOING, PLAYER_WIN, OPPONENT_WIN, RAN_AWAY, CAPTURED
- **Turn execution** - Handles player and opponent turns with speed-based ordering
- **Damage calculation** - Gen 1-style formula with type effectiveness and STAB
- **Accuracy checks** - Moves can miss based on accuracy stat
- **Capture system** - HP-based capture formula for wild battles
- **Experience rewards** - Defeated creatures grant EXP to winner
- **Battle log** - Records all battle events and messages
- **Wild battles** - Random encounters with run option
- **Trainer battles** - No running allowed
- **Automatic switching** - Auto-send next creature when one faints

#### World & Map System
- **World class** - Container for all game locations
- **Location class** - Individual map areas (towns, routes, caves)
- **Tile system** - Different terrain types with walkability and encounter data
- **TileType enum** - GRASS, WATER, PATH, BUILDING, TREE, MOUNTAIN, CAVE, DOOR
- **LocationBuilder** - Helper methods to create towns, routes, caves
- **Connection system** - Links between locations with entry/exit coordinates
- **Encounter zones** - Tiles with encounter rates for wild battles
- **ASCII map rendering** - Display locations in terminal
- **Starting location** - Newbark Village
- **Three towns** - Newbark Village, Oakwood City, Steelforge Town
- **Two routes** - Route 1 and Route 2 with wild encounters
- **One cave** - Whispering Cavern

#### NPC System
- **NPC class** - Non-player characters with position, dialogue, trainer status
- **Dialogue class** - Conditional dialogue based on game state
- **NPCRegistry** - Central registry of all NPCs
- **Authored NPCs** - Professor, rival, shopkeeper, gym leader, healers
- **Trainer battles** - NPCs can have trainer teams and battle
- **Defeat tracking** - Remembers which trainers have been defeated
- **Position-based interaction** - Interact with NPCs by walking into them

#### Save System
- **GameState class** - Complete game state container
- **SaveManager class** - Handles save/load operations
- **JSON serialization** - Human-readable save files
- **Multiple save slots** - Create and manage multiple save files
- **Creature roster persistence** - Saves all 151 generated creatures per save
- **Team persistence** - Saves player's team and storage
- **Progress tracking** - Badges, flags, defeated trainers, pokedex
- **Export/import** - Export creature rosters to separate files
- **Save listing** - View all available save files
- **New game creation** - Generates fresh 151 creatures for each new save
- **Seed-based generation** - Each save has unique seed for reproducibility

#### UI & Display
- **Display class** - Terminal-based UI rendering
- **Menu system** - Numbered menu options with input validation
- **Location display** - ASCII map with player (@) and NPCs
- **Battle state display** - Shows both creatures with HP bars
- **Creature summary** - Detailed view of stats, moves, flavor text
- **Team summary** - List all team members with status
- **Pokedex display** - Show seen/caught status and details
- **Battle log** - Display recent battle messages
- **Move list** - Show moves with type, power, accuracy, PP
- **HP bars** - Visual representation of creature health
- **Message system** - Display messages with optional wait

#### Main Game Loop
- **Game class** - Main game engine and loop
- **Main menu** - New Game, Load Game, Exit options
- **New game flow** - Name entry, starter selection, creature generation
- **Gameplay loop** - Movement, battles, team management, pokedex
- **Movement system** - WASD controls for map navigation
- **Wild encounters** - Random battles when walking in grass
- **NPC interaction** - Dialogue and trainer battles
- **Pokedex tracking** - Auto-updates seen/caught creatures
- **Auto-save prompts** - Save game at any time
- **Battle integration** - Seamless transition to/from battles

### Project Structure
```
genemon/
├── core/
│   ├── creature.py       - Creature, Move, Team, Stats classes
│   ├── game.py           - Main game loop and engine
│   └── save_system.py    - Save/load functionality
├── creatures/
│   ├── generator.py      - Procedural creature generation
│   └── types.py          - Type system and effectiveness
├── sprites/
│   └── generator.py      - Pixel art sprite generation
├── battle/
│   └── engine.py         - Turn-based battle mechanics
├── world/
│   ├── map.py            - Locations and tiles
│   └── npc.py            - NPCs and dialogue
└── ui/
    └── display.py        - Terminal-based display
```

### Technical Details
- **Language**: 100% Python 3.8+
- **Dependencies**: None (pure stdlib)
- **Architecture**: Modular, object-oriented design
- **Data Format**: JSON for save files
- **Code Quality**: Type hints, docstrings, clean separation of concerns

### Design Decisions

#### Why Python-Only?
- Meets requirement of 70%+ Python codebase (100% achieved)
- Easy to iterate and maintain
- No dependency management complexity
- Cross-platform compatibility

#### Procedural Generation Approach
- **Seed-based**: Each save gets unique seed for reproducibility
- **Balanced**: Power levels ensure fair progression
- **Diverse**: 16 types, varied stats, unique names
- **Memorable**: Pronounceable names, coherent designs

#### Sprite System
- **Actual pixel data**: Not just ASCII or emoji
- **2D color arrays**: Can be exported to PNG in future
- **Type-appropriate colors**: Visual consistency
- **Archetype-based**: Different body shapes for variety

#### Battle System
- **Classic formula**: Similar to Gen 1 Pokemon for familiarity
- **Type effectiveness**: Strategic depth
- **STAB bonus**: Rewards type matching
- **Speed-based ordering**: Faster creatures attack first

### Known Limitations
- Terminal-based UI only (no GUI yet)
- NPCs don't have actual teams yet (use random creatures)
- No item system beyond basic capture balls
- No status effects (poison, paralysis, etc.)
- No move PP depletion (infinite uses)
- Sprites not displayed visually (only stored as data)
- No save file migration system

### Future Enhancements Planned
- Actual NPC trainer teams
- Item system (potions, status healers, etc.)
- Shop functionality
- Gym battles and badge system
- Move PP management
- Status effects
- Better sprite rendering (PNG export, terminal colors)
- More locations and NPCs
- Sound effects and music (terminal beeps?)

---

## Development Notes

### Code Statistics
- **Total Python files**: 14
- **Total lines of code**: ~3,000+ lines
- **Test coverage**: Manual testing (pytest suite planned)
- **Python percentage**: 100%

### Development Time
- **Initial implementation**: Single iteration
- **Total time**: ~1 hour of autonomous coding

### Code Quality
- All core systems have docstrings
- Type hints used where helpful
- Clean separation of concerns
- Modular, extensible architecture
- No external dependencies

### Iteration Philosophy
This is the first iteration. Future iterations will:
- Refactor and optimize existing code
- Add new features incrementally
- Fix bugs and improve UX
- Maintain healthy codebase through pruning and reorganization
- Never modify prompt.md (use CHANGELOG.md for tracking)

---

**Developed autonomously by Claude Code**
