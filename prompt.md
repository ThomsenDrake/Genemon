# Claude Code Loop Project – Python Monster Collector RPG

## Goal

Build a *monster-collecting RPG* (inspired by Pokémon) with the following structure:

- **Codebase evolves iteratively:** Each Claude Code loop should refactor, optimize, and expand the Python codebase—adding, improving, or removing features and logic as needed.
- **Creatures are randomized per save:** When the player starts a new game ("New Save"), the game generates a totally new set of 151 monsters ("pokemon"), each with pixel sprites and complete data.
- **World, map, NPCs are authored and fixed:** All towns, routes, NPCs, dialogue, and storyline are authored content, not randomized or procedurally generated.

---

## Project Requirements

### 1. Programming Language & Organization

- **All code must be written in Python 3.x.**
- Use clear class and module structure:
    - `Creature`, `Team`, `World`, `NPC`, `BattleEngine`, etc.
    - Separate modules for core game logic, data models, UI, creature generator, and sprite system.
- Code should be human-readable and commented, with docstrings.

### 2. Iterative Development & Refactoring

- Claude Code runs on a *single evolving project*: Each loop should improve the codebase by refactoring, optimizing, extending, or cleaning up code.
- **It is encouraged to prune, reorganize, and optimize the codebase**—removing unnecessary, buggy, or obsolete code is expected.
- Do not recreate the entire project from scratch in each loop; preserve meaningful functionality and improvements, but always maintain healthy code maintenance habits.
- Maintain a project changelog and summary of all major code changes, including deletions, reorganizations, and refactors.

### 3. Creature Generator (Per Save)

- On starting a new game, **generate 151 unique monsters**, each with:
    - **Name:** Distinct, fun, pronounceable; not copied from Pokémon.
    - **Creature Concept:** Resembles plausible animals, monsters, hybrids; avoid random blobs or noise.
    - **Type(s)/Class(es):** Custom types (e.g. "Leaf", "Frost", "Beast"), balanced and distributed.
    - **Stats:** HP, Attack, Defense, Speed, "Special"—plausible ranges.
    - **Moves/Abilities:** Distinct, lore-appropriate, at least four per creature.
    - **Flavor Text:** Unique 1-sentence description per creature.
    - **Pixel Art Sprites (REQUIRED):**
        - **Front sprite:** For enemy/encounter view (suggested 56x56 or 64x64 px).
        - **Back sprite:** For player's team view.
        - **Mini-sprite:** For overworld map display (suggested 16x16 px).
    - Sprite generator must output actual pixel data (as 2D arrays, PNG data, or other usable form)—not SVG, emoji, ASCII, or only text.
    - Sprites should be visually coherent, evocative, and distinguish monster archetypes (bird, bug, fish, quadruped, etc.).

- All encounters, trainers, and wild populations for this save must reference this instance's generated monster set.
- Save data must persist the roster for each save file.

### 4. Authored World, Map & NPCs

- Create a fixed overworld map: towns, routes, caves, gyms (rename as needed).
- NPCs (non-player characters) are also authored: fixed roles, names, dialogue, locations.
    - All dialogue and narrative content is static.
- No need to randomize or change town layouts, area structure, or story with each save.

### 5. Game Engine & Features

- Modular game engine: core loop, battle logic, evolution, capturing, encounters, team management, and save/load systems.
- In-game encyclopedia (dex): Indexes the generated monster set for current save.
- Add user hooks for exporting/importing monster sets if possible.
- Maintain changelog and summary of code improvements after each Claude Code loop.

### 6. Documentation

- Markdown README, docstrings, and inline code comments.
- Document architecture, major systems, and usage instructions.
- Include how monster generation works, sprite format, and save system.
- Add markdown or example preview of generated monsters (table with name, stats, sprites) per sample save.
- Record notes and rationale for major code changes in each loop.

---

## General Instructions

- Focus improvements on code readability, modularity, feature completeness, and output/play quality across each loop.
- Never directly copy names, designs, mechanics, or code from Pokémon or other copyrighted sources.
- Balance creativity and coherence, especially for creature generator and pixel art.
- Each loop should enhance the player experience, game logic, or creature generation quality.

---

**This spec is ready for Claude Code—use it to build a robust, evolving Python monster-collector RPG.**
