# Genemon - Quick Start Guide

## Installation

No installation needed! Genemon uses only Python's standard library.

### Requirements
- Python 3.8 or higher
- Terminal/console access

### Verify Python Version
```bash
python3 --version
```

Should output Python 3.8 or higher.

## Running the Game

```bash
# Navigate to the project directory
cd loop

# Run the game
python3 main.py
```

## First Time Setup

### Step 1: Create a New Game
1. Select **"1. New Game"** from the main menu
2. Enter your **player name** (or press Enter for "Player")
3. Enter a **save file name** (or press Enter for "save1")

### Step 2: Choose Your Starter
You'll be presented with three starter creatures:

- **Starter 1** - Flame type (strong vs Leaf, weak vs Aqua)
- **Starter 2** - Aqua type (strong vs Flame, weak vs Leaf)
- **Starter 3** - Leaf type (strong vs Aqua, weak vs Flame)

Enter **1**, **2**, or **3** to choose.

### Step 3: Wait for Generation
The game will generate **151 unique creatures** with:
- Unique names
- Stats and types
- Moves and abilities
- Pixel art sprites

This takes about 10-15 seconds.

### Step 4: Start Your Adventure!
You'll begin in **Newbark Village** with your chosen starter.

## Basic Controls

### Movement
When prompted "What do you want to do?":
1. Select **"1. Move"**
2. Enter direction:
   - **W** - Move up
   - **S** - Move down
   - **A** - Move left
   - **D** - Move right
   - **X** - Cancel

### Main Menu Options
1. **Move** - Navigate the map
2. **Team** - View and manage your creatures
3. **Pokedex** - View creatures you've seen and caught
4. **Save** - Save your progress
5. **Quit to Menu** - Return to main menu

### During Battle
1. **Attack** - Choose a move to use
2. **Team** - Switch to a different creature
3. **Capture** - Try to catch a wild creature (wild battles only)
4. **Run** - Attempt to flee (wild battles only)

## Your First Adventure

### 1. Explore Newbark Village
- Walk around using WASD controls
- Talk to NPCs by walking into them
- Find the **Professor** (P) and **Healer** (H)

### 2. Travel to Route 1
- Walk to the bottom exit of town
- Route 1 has **wild creatures** in the grass (`.` tiles)

### 3. Wild Encounters
- Walking on grass tiles has a chance to trigger battles
- You'll see: `A wild [CreatureName] appeared!`
- Try **capturing** some creatures to build your team!

### 4. Build Your Team
- You can carry up to **6 creatures** at once
- Catch different types for variety
- Level up your team by battling

### 5. Continue Exploring
- Travel through Route 1 to reach **Oakwood City**
- Fight **trainers** along the way (you can't run from these!)
- Explore more areas and complete your Pokedex

## Tips & Tricks

### Type Effectiveness
- **Super Effective (2x damage)**: Use type advantages!
  - Flame > Leaf, Frost, Insect, Metal
  - Aqua > Flame, Terra
  - Leaf > Aqua, Terra
  - Volt > Aqua, Gale
  - And more!

- **Not Very Effective (0.5x damage)**: Avoid these matchups
  - Flame < Aqua, Terra
  - Aqua < Leaf, Frost
  - Leaf < Flame, Toxin

### Battle Strategy
1. **STAB Bonus**: Moves that match your creature's type do 1.5x damage
2. **Speed Matters**: Faster creatures attack first
3. **Type Coverage**: Build a team with diverse types
4. **Level Up**: Higher level = higher stats

### Catching Creatures
- **Lower HP = Higher Catch Rate**: Weaken creatures before catching
- **Capture Balls**: You start with 10, use them wisely
- **Build a Collection**: Try to catch all 151!

### Saving Your Game
- Select **"4. Save"** from the main menu
- Save frequently to preserve your progress
- Your entire creature roster is saved per file

## Pokedex

View your Pokedex to see:
- **Seen**: Creatures you've encountered (listed)
- **Caught**: Creatures you've captured (full details)

Enter a creature number (1-151) to view details.

## Example Play Session

```
1. Start game, name yourself "Ash", choose Flame starter
2. Explore Newbark Village, talk to Professor
3. Head south to Route 1
4. Encounter wild creatures in grass
5. Catch 2-3 different creatures
6. Level up your team by battling
7. Reach Oakwood City
8. Save your game
9. Continue exploring!
```

## Troubleshooting

### Game Won't Start
- Check Python version: `python3 --version`
- Ensure you're in the `loop` directory
- Try: `python3 -m py_compile main.py` to check for errors

### Can't See Creatures
- This version displays creature data but not visual sprites
- Sprites are generated and stored, future versions will display them

### Lost in Battle
- If you lose, you'll return to the starting town
- Your team will be fully healed
- No progress is lost!

### Want to Start Over
- Create a new game with a different save name
- Each save generates a completely new set of 151 creatures!

## Next Steps

- Complete your team of 6 creatures
- Explore all locations (towns, routes, caves)
- Battle all trainers
- Complete your Pokedex (see all 151, catch all 151)
- Challenge the Gym Leader in Steelforge Town

## Need Help?

See `genemon/README.md` for complete documentation on:
- Architecture and code structure
- Creature generation details
- Save file format
- Future features

---

**Enjoy your unique Genemon adventure!**
