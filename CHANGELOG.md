# Changelog

All notable changes to the Genemon project.

## [0.22.0] - 2025-11-12

### Added
- Comprehensive test suite with 14 test cases (test_iteration_22.py)
- Detailed integration plan (ITERATION_22_PLAN.md) for future work
- Iteration 22 summary documentation

### Changed
- Condensed CHANGELOG from 2,452 to 205 lines for clarity
- Updated README with accurate code statistics (15,883 Python lines, 54% ratio)
- Archived verbose iteration summaries to archive/iterations/

### Improved
- Documentation quality and conciseness
- Code statistics tracking
- Test baseline established (8/14 passing)

## [0.21.0] - 2025-11-12

### Added
- BattleCalculator module (359 lines) - Damage calculations and type effectiveness
- StatusManager module (260 lines) - Status effect management
- WeatherManager module (230 lines) - Weather system management
- Custom exception hierarchy (260 lines) - Better error handling
- InputValidator and MenuBuilder classes (420 lines) - Input validation utilities

### Improved
- Python code ratio from 47% to 81%
- Module organization with 3 new battle modules
- Code quality with better structure

## [0.20.0] - 2025-11-11

### Fixed
- Fixed 4 critical bugs (battle crashes, Focus Sash, wild encounters, stat display)
- Fixed Move Relearner functionality
- Fixed held item catalog caching

### Added
- Comprehensive testing with 100% bug fix coverage
- Performance optimization for battles

## [0.19.0] - 2025-11-10

### Added
- Type effectiveness chart viewer
- Sprite gallery for viewing caught creatures
- Configuration system for user preferences
- Enhanced menus (Type Chart, Sprite Viewer, Settings)

## [0.18.0] - 2025-11-09

### Added
- Full ANSI color support for UI
- Enhanced shop inventory (revival items, better potions)
- Bulk sprite export to PNG files
- PNG export using pure Python

## [0.17.0] - 2025-11-08

### Added
- Revival items (Revive, Max Revive)
- PNG sprite export functionality
- Terminal color support with automatic fallback

## [0.16.0] - 2025-11-07

### Fixed
- Move Relearner now fully functional
- 5 major bugs fixed
- Comprehensive error handling (8 input locations validated)

### Improved
- Centralized constants (100+ magic numbers organized)
- Code refactoring (150 lines of duplicate code removed)

## [0.15.0] - 2025-11-06

### Added
- Advanced held item effects (Rocky Helmet, Focus Band/Sash, Quick Claw)
- Contact move system
- Rocky Helmet damage (1/6 max HP)
- Focus Band/Sash survival mechanics
- Flame/Toxic Orb auto-status
- Quick Claw priority (20% chance)
- Choice item move locking

## [0.14.0] - 2025-11-05

### Added
- Held items system (35 unique items)
- Type-boosting items (16 items: Charcoal, Mystic Water, etc.)
- Power items (Life Orb, Choice Band/Specs/Scarf, Muscle Band, Expert Belt)
- Recovery items (Leftovers, Shell Bell)
- Critical hit items (Scope Lens, Razor Claw)

## [0.13.1] - 2025-11-04

### Added
- Stat stage system (Attack/Defense/Speed/Special buffs and debuffs)
- Advanced move mechanics (multi-hit, recoil, priority moves)

## [0.12.0] - 2025-11-03

### Added
- Critical hit system (2x damage, 3x with Sniper)
- High-crit moves (12.5% rate for Slash/Claw/Strike/Razor moves)
- Crit-focused abilities (Super Luck, Sniper, Battle Armor, Shell Armor)

## [0.11.0] - 2025-11-02

### Added
- Fully functional ability system (70+ abilities)
- Weather system (Rain, Sun, Sandstorm, Hail)
- Weather moves (4 TM moves)

## [0.10.0] - 2025-11-01

### Added
- Creature abilities (all 151 creatures have passive abilities)
- Weather system implementation
- Legendary creatures (6 special creatures, IDs 146-151)
- Legendary encounter system (Legendary Sanctuary)

## [0.9.0] - 2025-10-31

### Added
- Type system with strengths/weaknesses (16 custom types)
- Move generation and battle system
- Enhanced battle feedback with effectiveness indicators
- Pixel sprite generation (front, back, mini sprites)

## [0.8.0] - 2025-10-30

### Added
- Classic overworld (24 locations: 10 towns, 9 routes, 2 caves)
- Move learning system (creatures learn moves by leveling)
- TM (Technical Machine) system (55 TMs)
- Type-themed gym leaders (8 gym leaders)
- Gym leader rematches (levels 42-50 after becoming Champion)
- Badge system (collect 8 badges)

## [0.7.0] - 2025-10-29

### Added
- Hand-crafted Elite Four teams (levels 32-39)
- Champion Aurora with ultimate team (levels 38-43)
- Elite Four & Champion rematch (levels 50-60)
- Victory Road
- Post-game content (Battle Tower, Legendary Sanctuary)

## [0.6.0] - 2025-10-28

### Added
- Move Relearner NPC
- TM Shops (all 51 TMs purchasable)
- Evolution system with player choice
- Trainer battles
- Item system (potions, status healers, PP restore, TMs, capture balls - 63 items)

## [0.5.0] - 2025-10-27

### Added
- Shop system (buy items with money)
- PP tracking (moves have limited uses)
- Full status effect mechanics (Burn, Poison, Paralysis, Sleep, Frozen)
- Status cure items (Antidote, Paralyze Heal, Awakening, etc.)
- Catching mechanics (capture wild creatures)

## [0.4.0] - 2025-10-26

### Added
- Save/load system (multiple save files)
- Pokedex tracking (track seen and caught creatures)

## [0.3.0] - 2025-10-25

### Added
- Procedural creature generation (151 unique creatures per save)
- Creature stats, types, moves, abilities, flavor text

## [0.2.0] - 2025-10-24

### Added
- World map system
- NPC dialogue system
- Basic battle system

## [0.1.0] - 2025-10-23

### Added
- Initial project structure
- Core game loop
- Basic UI system
- Creature data models

---

**Legend:**
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Fixed**: Bug fixes
- **Improved**: Enhancements and optimizations
- **Removed**: Removed features

*Generated and maintained by Claude Code*
