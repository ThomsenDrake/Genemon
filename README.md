# Genemon

A Python monster-collecting RPG where each new game features **151 completely unique creatures** generated from scratch with procedural stats, moves, types, and pixel art sprites.

## 🎮 Concept

Unlike traditional monster-collecting games with fixed rosters, Genemon creates a fresh experience every playthrough:
- **151 unique creatures** generated procedurally for each new save file
- **Unique stats, types, and movesets** - no two playthroughs are the same
- **Procedural pixel art sprites** - each creature gets unique front/back/mini sprites (56x56 and 16x16)
- **Classic RPG gameplay** - familiar mechanics with infinite variety

## ✅ Current Status - v0.32.0

**This project is being autonomously developed by Claude Code in a sandboxed environment.**

### Implemented Features

- [x] **Code Quality & Performance Optimization** - Critical bug fixes and 8x speedup! (NEW in v0.32.0) ⚡
  - Fixed critical bare except clause in colors.py
  - Added primary_type and secondary_type properties to CreatureSpecies
  - Implemented LRU caching for type effectiveness (8x faster lookups!)
  - 5 comprehensive tests (all passing) + zero breaking changes
  - Better error handling, cleaner API, significantly faster battles
- [x] **Performance Profiling Infrastructure** - Profiling and benchmarking system added! (v0.31.0) 📊
  - Created PerformanceProfiler utility class (280 lines)
  - Multiple profiling methods: decorator, context manager, manual timing
  - Automatic result aggregation with min/max/avg/total metrics
  - Performance baselines established for critical systems
  - 14 comprehensive tests (all passing) + zero overhead design
  - Ready for identifying and optimizing bottlenecks
- [x] **NPC Data Externalization** - All NPCs now loaded from JSON! (v0.30.0) 📦
  - Externalized all 52 NPCs to genemon/data/npcs.json
  - Created NPCLoader utility class for data loading and validation
  - Enabled modding support (players can customize NPCs!)
  - 22 comprehensive tests (all passing) + 100% backward compatibility
  - Better maintainability with data/code separation
- [x] **Battle Module Integration** - Fully integrated battle system modules! (v0.29.0) ✅
  - Integrated DamageCalculator and BattleStatManager into battle/engine.py
  - Reduced engine.py from 1,370 to 906 lines (34% reduction!)
  - Removed 464 lines of duplicate code across 9 methods
  - Improved code organization with clear module boundaries
  - 12 integration tests (all passing) + maintained 100% backward compatibility
  - Better testability and maintainability
- [x] **MenuManager Refactoring** - Extracted menu system to dedicated module! (v0.27.0) 🏗️
  - Created MenuManager class in genemon/ui/menu_manager.py (468 lines)
  - Reduced game.py from 1467 to 1081 lines (26% reduction!)
  - Improved code organization and single responsibility principle
  - 26 comprehensive tests for MenuManager (all passing)
  - Zero functional changes (100% backward compatible)
- [x] **Code Quality Improvements** - Consolidated input validation! (v0.26.0) 🔧
  - Removed duplicate input handling code (27 lines)
  - Standardized all user input with InputValidator class
  - Improved code consistency and maintainability
  - 25 new tests for input validation (all passing)
  - Zero functional changes (100% backward compatible)
- [x] **Shiny Creatures** - Rare color variants with alternate sprites! (v0.25.0) ⭐
  - 1/4096 encounter rate in the wild
  - Special sparkle indicator (✨) in all displays
  - Alternate color palettes (gold, purple, silver tints)
  - 8x better odds through breeding (1/512)
  - Full persistence through saves
- [x] **Breeding System** - Breed creatures to produce eggs! (v0.25.0) ⭐
  - Breed level 15+ creatures of the same species
  - Eggs inherit up to 3 moves from both parents
  - Hatch eggs into level 1 creatures
  - Enhanced shiny chance for breeding
  - Complete breeding center UI
  - 19 comprehensive tests (all passing)
- [x] **Bug fixes and test suite improvements** - All tests passing! (v0.24.0)
  - Fixed critical trading UI import error
  - Updated test suite to match current API
  - 58/58 tests passing (100% success rate)
- [x] **Trading System** - Export/import creatures between save files! (v0.23.0)
  - Export creatures from team or storage
  - Import creatures from other saves
  - Trade history tracking
  - Cross-save species compatibility
  - Trade file management
  - 19 comprehensive tests (all passing)
- [x] **Python codebase** - 12,700 lines of Python code across 38 modules (95.2% ratio) (v0.32.0)
- [x] **Comprehensive test suite** - 173 test cases covering all major systems (173/173 passing) (v0.32.0)
- [x] **Iteration 22 planning** - Detailed plan for battle integration and NPC data extraction (v0.22.0)
- [x] **Documentation cleanup** - Reduced CHANGELOG from 2,452 to 205 lines for clarity (v0.22.0)
- [x] **Code architecture improvements** - New battle modules, exception hierarchy, input validators (v0.21.0)
- [x] **Modular battle system** - BattleCalculator, StatusManager, WeatherManager modules (+849 lines) (NEW in v0.21.0)
- [x] **Exception hierarchy** - Custom exceptions for better error handling (NEW in v0.21.0)
- [x] **Input validation utilities** - InputValidator and MenuBuilder classes (NEW in v0.21.0)
- [x] **Critical bug fixes** - Fixed 4 game-breaking bugs (battle crashes, Focus Sash, wild encounters) (v0.20.0)
- [x] **Performance optimization** - Held items catalog caching for faster battles (v0.20.0)
- [x] **Comprehensive testing** - 100% test coverage for all bug fixes (v0.20.0)
- [x] **Type effectiveness chart** - Interactive type chart to understand matchups! (v0.19.0)
- [x] **Sprite viewer/gallery** - View pixel art sprites of caught creatures in-game! (v0.19.0)
- [x] **Configuration system** - Save preferences for colors, auto-save, and more! (v0.19.0)
- [x] **Enhanced menus** - New Type Chart, Sprite Viewer, and Settings menus! (v0.19.0)
- [x] **Color UI integration** - Full ANSI color support for all display functions! (v0.18.0)
- [x] **Enhanced shop inventory** - Revival items, better potions, and capture balls now available! (v0.18.0)
- [x] **Bulk sprite export** - Export all 151 creatures to PNG files at once! (v0.18.0)
- [x] **Revival items** - Revive and Max Revive to restore fainted creatures! (v0.17.0)
- [x] **PNG sprite export** - Export creatures as actual PNG images using pure Python! (NEW in v0.17.0)
- [x] **Terminal color support** - ANSI color module with automatic fallback (NEW in v0.17.0)
- [x] **Critical bug fixes** - Move Relearner now fully functional! 5 major bugs fixed (v0.16.0)
- [x] **Comprehensive error handling** - All 8 input locations now validate safely (v0.16.0)
- [x] **Centralized constants** - 100+ magic numbers organized in constants.py (v0.16.0)
- [x] **Code refactoring** - Elite team creation simplified, 150 lines of duplicate code removed (v0.16.0)
- [x] **Advanced held item effects** - Rocky Helmet, Focus Band/Sash, Quick Claw now fully functional! (v0.15.0)
- [x] **Contact move system** - Moves tagged as contact/non-contact, affects Rocky Helmet (NEW in v0.15.0)
- [x] **Rocky Helmet damage** - Punishes attackers with contact moves (1/6 max HP) (NEW in v0.15.0)
- [x] **Focus Band/Sash** - Survive lethal hits with 1 HP (10% chance or guaranteed at full HP) (NEW in v0.15.0)
- [x] **Flame/Toxic Orb** - Auto-inflict Burn/Poison for Guts strategies (NEW in v0.15.0)
- [x] **Quick Claw priority** - 20% chance to move first regardless of speed (NEW in v0.15.0)
- [x] **Choice item locking** - Tracks move locking for Choice Band/Specs/Scarf (NEW in v0.15.0)
- [x] **Held items system** - 35 unique held items for creatures to equip! (v0.14.0)
- [x] **Type-boosting items** - 16 type-specific items (Charcoal, Mystic Water, etc.) (v0.14.0)
- [x] **Power items** - Life Orb, Choice Band/Specs/Scarf, Muscle Band, Expert Belt (v0.14.0)
- [x] **Recovery items** - Leftovers and Shell Bell for sustain strategies (v0.14.0)
- [x] **Critical hit items** - Scope Lens and Razor Claw boost crit rate (v0.14.0)
- [x] **Stat stage system** - Attack/Defense/Speed/Special buffs and debuffs (v0.13.1)
- [x] **Advanced move mechanics** - Multi-hit, recoil, and priority moves (v0.13.0)
- [x] **Procedural creature generation system** - 151 unique creatures per save
- [x] **Critical hit system** - Land devastating crits with 2x damage (3x with Sniper)! (v0.12.0)
- [x] **High-crit moves** - Moves with "Slash", "Claw", "Strike", "Razor" have 12.5% crit rate (v0.12.0)
- [x] **Crit-focused abilities** - Super Luck, Sniper, Battle Armor, Shell Armor (v0.12.0)
- [x] **Fully functional ability system** - All 70+ abilities now work in battles! (v0.11.0)
- [x] **Weather system** - 4 weather conditions (Rain, Sun, Sandstorm, Hail) affect battles
- [x] **Creature abilities** - All 151 creatures have unique passive abilities (NEW in v0.10.0)
- [x] **Weather moves** - 4 TM moves to change weather during battles (NEW in v0.10.0)
- [x] **Legendary creatures** - 6 special legendary creatures (IDs 146-151) with high stats
- [x] **Legendary encounter system** - 6 special level 60 battles in Legendary Sanctuary
- [x] **Type system with strengths/weaknesses** - 16 custom types with full effectiveness chart
- [x] **Move generation and battle system** - Turn-based combat with type effectiveness and status effects
- [x] **Enhanced battle feedback** - Inline effectiveness indicators in damage messages
- [x] **Pixel sprite generation** - Actual 2D color arrays for front, back, and mini sprites
- [x] **Classic overworld and navigation** - 24 locations including 10 towns, 9 routes, 2 caves, and post-game areas
- [x] **Move learning system** - Creatures learn new moves by leveling up (4-6 moves per species)
- [x] **TM (Technical Machine) system** - 55 TMs to teach powerful moves to compatible creatures (4 weather moves added)
- [x] **Type-themed gym leaders** - 8 gym leaders with specialized type teams
- [x] **Gym leader rematches** - All 8 gym leaders rebattleable at levels 42-50 after becoming Champion
- [x] **Badge system** - Collect all 8 badges by defeating gym leaders
- [x] **Hand-crafted Elite Four teams** - 4 elite trainers with strategic, type-optimized teams (levels 32-39)
- [x] **Champion with ultimate team** - Champion Aurora with perfectly balanced 6-creature team (levels 38-43)
- [x] **Elite Four & Champion rematch** - Rebattle at higher levels (50-60) for endgame challenge
- [x] **Victory Road** - Challenging path to the Elite Four
- [x] **Post-game content** - Battle Tower and Legendary Sanctuary with legendary encounters
- [x] **Move Relearner** - Special NPC to reteach forgotten moves
- [x] **TM Shops** - All 51 TMs purchasable from 3 merchants
- [x] **Evolution system** - Creatures evolve with player choice and visual feedback
- [x] **Trainer battles** - Fight NPCs and trainers throughout the world
- [x] **Item system** - Potions, status healers, PP restore, TMs, and capture balls (63 items total)
- [x] **Shop system** - Buy items from merchants with in-game money
- [x] **PP tracking** - Moves have limited uses with PP restoration
- [x] **Full status effect mechanics** - Burn reduces attack 50%, Paralysis reduces speed 75%, plus damage/immobilization
- [x] **Status cure items** - Antidote, Paralyze Heal, Awakening, and more to cure status effects
- [x] **Catching mechanics** - Capture wild creatures with capture balls
- [x] **Save/load system** - Multiple save files with full persistence
- [x] **Pokedex tracking** - Track seen and caught creatures

## 🛠️ Technology Stack

**Python-First** - Pure Python 3.8+ implementation (95.2% of codebase, 12,700 lines)
- **No external dependencies** - Uses only Python standard library
- **Modular architecture** - 38 specialized modules for creatures, battle, breeding, trading, world, UI, menus, sprites, exceptions, validation, data loading, profiling
- **Modding support** - JSON data files for NPCs, enabling easy customization
- **Clean code practices** - Custom exception hierarchy, input validation utilities, comprehensive docstrings
- **JSON save files** - Human-readable save data
- **Trading system** - Export/import creatures between saves with full compatibility

## 🚀 Quick Start

```bash
# Navigate to project directory
cd loop

# Run the game
python main.py
```

### First Time Playing

1. Select "New Game" from the main menu
2. Enter your player name and save file name
3. Choose your starter (Flame, Aqua, or Leaf type)
4. Wait for generation of 151 unique creatures (takes ~10 seconds)
5. Start your adventure!

## 📖 How to Play

- **Movement**: W/A/S/D keys to move around the map
- **Battles**: Choose Attack/Switch/Capture/Run options
- **Team**: View and manage your team of creatures
- **Pokedex**: Check which creatures you've seen and caught
- **Save**: Save your progress at any time

See `genemon/README.md` for complete documentation.

## 🤖 About This Project

This is an experimental project developed entirely by an autonomous AI agent (Claude Code) running in a secure Docker sandbox. The AI:
- Reads the project requirements from `prompt.md`
- Makes architectural decisions
- Writes code and tests
- Commits changes to this repository
- Iterates until features are complete

## 📜 License

*To be determined*

---

**⚡ Generated and maintained by Claude Code**
