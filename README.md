# Genemon

A Python monster-collecting RPG where each new game features **151 completely unique creatures** generated from scratch with procedural stats, moves, types, and pixel art sprites.

## 🎮 Concept

Unlike traditional monster-collecting games with fixed rosters, Genemon creates a fresh experience every playthrough:
- **151 unique creatures** generated procedurally for each new save file
- **Unique stats, types, and movesets** - no two playthroughs are the same
- **Procedural pixel art sprites** - each creature gets unique front/back/mini sprites (56x56 and 16x16)
- **Classic RPG gameplay** - familiar mechanics with infinite variety

## ✅ Current Status - v0.14.0

**This project is being autonomously developed by Claude Code in a sandboxed environment.**

### Implemented Features

- [x] **Held items system** - 35 unique held items for creatures to equip! (NEW in v0.14.0)
- [x] **Type-boosting items** - 16 type-specific items (Charcoal, Mystic Water, etc.) (NEW in v0.14.0)
- [x] **Power items** - Life Orb, Choice Band/Specs/Scarf, Muscle Band, Expert Belt (NEW in v0.14.0)
- [x] **Recovery items** - Leftovers and Shell Bell for sustain strategies (NEW in v0.14.0)
- [x] **Critical hit items** - Scope Lens and Razor Claw boost crit rate (NEW in v0.14.0)
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

**100% Python** - Pure Python 3.8+ implementation
- **No external dependencies** - Uses only Python standard library
- **Modular architecture** - Separate modules for creatures, battle, world, UI, sprites
- **JSON save files** - Human-readable save data

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
