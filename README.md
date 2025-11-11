# Genemon

A Python monster-collecting RPG where each new game features **151 completely unique creatures** generated from scratch with procedural stats, moves, types, and pixel art sprites.

## 🎮 Concept

Unlike traditional monster-collecting games with fixed rosters, Genemon creates a fresh experience every playthrough:
- **151 unique creatures** generated procedurally for each new save file
- **Unique stats, types, and movesets** - no two playthroughs are the same
- **Procedural pixel art sprites** - each creature gets unique front/back/mini sprites (56x56 and 16x16)
- **Classic RPG gameplay** - familiar mechanics with infinite variety

## ✅ Current Status - v0.1.0 (Initial Release)

**This project is being autonomously developed by Claude Code in a sandboxed environment.**

### Implemented Features

- [x] **Procedural creature generation system** - 151 unique creatures per save
- [x] **Type system with strengths/weaknesses** - 16 custom types with full effectiveness chart
- [x] **Move generation and battle system** - Turn-based combat with type effectiveness
- [x] **Pixel sprite generation** - Actual 2D color arrays for front, back, and mini sprites
- [x] **Classic overworld and navigation** - Towns, routes, caves with ASCII map display
- [x] **Trainer battles** - Fight NPCs throughout the world
- [x] **Evolution chains** - Creatures evolve at specific levels
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
