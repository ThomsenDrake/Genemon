"""
Battle engine with turn-based combat mechanics.
"""

import random
from typing import Optional, List, Tuple
from enum import Enum
from ..core.creature import Creature, Move, Team, StatusEffect
from ..creatures.types import get_effectiveness
from ..core.held_items import (
    EFFECT_POWER_BOOST, EFFECT_TYPE_BOOST, EFFECT_DEFENSE_BOOST,
    EFFECT_SPEED_BOOST, EFFECT_CRIT_BOOST, EFFECT_STAT_HEAL,
    EFFECT_FOCUS_BAND, EFFECT_CHOICE_BOOST, EFFECT_LIFE_ORB,
    EFFECT_CONTACT_DAMAGE, EFFECT_AUTO_STATUS
)
from .damage_calculator import DamageCalculator
from .stat_manager import BattleStatManager


class BattleAction(Enum):
    """Types of battle actions."""
    ATTACK = "attack"
    SWITCH = "switch"
    ITEM = "item"
    RUN = "run"


class BattleResult(Enum):
    """Possible battle outcomes."""
    ONGOING = "ongoing"
    PLAYER_WIN = "player_win"
    OPPONENT_WIN = "opponent_win"
    RAN_AWAY = "ran_away"
    CAPTURED = "captured"


class Weather(Enum):
    """Weather conditions that affect battles."""
    NONE = "none"
    RAIN = "rain"          # Boosts Aqua moves, weakens Flame moves
    SUN = "sun"            # Boosts Flame moves, weakens Aqua moves
    SANDSTORM = "sandstorm"  # Damages non-Terra/Metal/Rock creatures each turn
    HAIL = "hail"          # Damages non-Frost creatures each turn


class BattleLog:
    """Stores messages from battle events."""

    def __init__(self):
        """Initialize battle log."""
        self.messages: List[str] = []

    def add(self, message: str):
        """Add a message to the log."""
        self.messages.append(message)

    def get_recent(self, count: int = 5) -> List[str]:
        """Get the most recent messages."""
        return self.messages[-count:]

    def clear(self):
        """Clear all messages."""
        self.messages.clear()


class Battle:
    """
    Main battle engine handling turn-based combat.
    """

    def __init__(
        self,
        player_team: Team,
        opponent_team: Team,
        is_wild: bool = False,
        can_run: bool = True
    ):
        """
        Initialize a battle.

        Args:
            player_team: Player's team
            opponent_team: Opponent's team (or wild creature)
            is_wild: True if battling a wild creature
            can_run: True if player can run from battle
        """
        self.player_team = player_team
        self.opponent_team = opponent_team
        self.is_wild = is_wild
        self.can_run = can_run

        # Validate both teams have at least one active creature
        self.player_active = player_team.get_first_active()
        self.opponent_active = opponent_team.get_first_active()

        if self.player_active is None:
            raise ValueError("Player team has no active creatures available for battle")
        if self.opponent_active is None:
            raise ValueError("Opponent team has no active creatures available for battle")

        self.log = BattleLog()
        self.result = BattleResult.ONGOING
        self.turn_count = 0

        # Weather system
        self.weather = Weather.NONE
        self.weather_turns = 0  # Number of turns weather lasts (0 = infinite until changed)

        # Initialize battle modules
        self.damage_calculator = DamageCalculator()
        self.stat_manager = BattleStatManager()

        # Reset one-time battle effects for all creatures
        for creature in self.player_team.creatures:
            creature.focus_sash_used = False
            creature.choice_locked_move = None
        for creature in self.opponent_team.creatures:
            creature.focus_sash_used = False
            creature.choice_locked_move = None

        # Battle start message
        if is_wild:
            self.log.add(f"A wild {self.opponent_active.species.name} appeared!")
        else:
            self.log.add("Battle started!")

        # Trigger on-entry abilities for both creatures
        self._trigger_on_entry_ability(self.player_active, True)
        self._trigger_on_entry_ability(self.opponent_active, False)

    def execute_turn(
        self,
        player_action: BattleAction,
        player_target: any = None
    ) -> BattleResult:
        """
        Execute one turn of battle.

        Args:
            player_action: Action player wants to take
            player_target: Target of action (move index, creature index, etc.)

        Returns:
            Current battle result
        """
        if self.result != BattleResult.ONGOING:
            return self.result

        self.turn_count += 1

        # Handle player action
        if player_action == BattleAction.RUN:
            if self._try_run():
                self.result = BattleResult.RAN_AWAY
                return self.result
        elif player_action == BattleAction.SWITCH:
            self._switch_creature(is_player=True, index=player_target)
        elif player_action == BattleAction.ATTACK:
            player_move = self._get_move_by_index(
                self.player_active,
                player_target
            )
            if player_move:
                # Get opponent's move (for priority checking)
                opponent_move = None
                usable_moves = [m for m in self.opponent_active.moves if m.pp > 0]
                if usable_moves:
                    opponent_move = random.choice(usable_moves)

                # Determine order based on priority first, then speed
                player_first = self._determine_order_with_priority(
                    player_move,
                    opponent_move
                )

                if player_first:
                    self._execute_attack(
                        self.player_active,
                        self.opponent_active,
                        player_move,
                        is_player=True
                    )
                    if not self.opponent_active.is_fainted():
                        self._opponent_turn_with_move(opponent_move)
                else:
                    self._opponent_turn_with_move(opponent_move)
                    if not self.player_active.is_fainted():
                        self._execute_attack(
                            self.player_active,
                            self.opponent_active,
                            player_move,
                            is_player=True
                        )

        # Check for fainted creatures
        self._check_fainted()

        # Process weather effects at end of turn
        self._process_weather()

        # Check win conditions
        self._check_battle_end()

        return self.result

    def _opponent_turn(self):
        """Execute opponent's turn (AI)."""
        if self.opponent_active.is_fainted():
            return

        # Simple AI: random move with PP
        usable_moves = [m for m in self.opponent_active.moves if m.pp > 0]
        if usable_moves:
            move = random.choice(usable_moves)
            self._execute_attack(
                self.opponent_active,
                self.player_active,
                move,
                is_player=False
            )
        else:
            # No PP left - use Struggle (a special move)
            self.log.add(f"{self.opponent_active.get_display_name()} has no PP left!")
            self._execute_struggle(self.opponent_active, self.player_active, is_player=False)

    def _opponent_turn_with_move(self, move: Optional[Move]):
        """Execute opponent's turn with a pre-selected move (for priority ordering)."""
        if self.opponent_active.is_fainted():
            return

        if move and move.pp > 0:
            self._execute_attack(
                self.opponent_active,
                self.player_active,
                move,
                is_player=False
            )
        else:
            # No PP left or no move - use Struggle
            self.log.add(f"{self.opponent_active.get_display_name()} has no PP left!")
            self._execute_struggle(self.opponent_active, self.player_active, is_player=False)

    def _execute_attack(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move,
        is_player: bool
    ):
        """Execute an attack move."""
        attacker_name = attacker.get_display_name()
        defender_name = defender.get_display_name()

        # Check if attacker can move (status effects)
        can_move, message = attacker.can_move()
        if not can_move:
            self.log.add(message)
            self._process_status_damage(attacker, defender)
            return

        # Check if move has PP
        if move.pp <= 0:
            self.log.add(f"{move.name} has no PP left!")
            self._execute_struggle(attacker, defender, is_player)
            return

        # Deduct PP
        move.pp -= 1

        self.log.add(f"{attacker_name} used {move.name}!")

        # Lock into move if using a Choice item
        if (attacker.held_item and attacker.held_item.effect_type == EFFECT_CHOICE_BOOST and
            attacker.choice_locked_move is None):
            attacker.choice_locked_move = move.name
            # Note: We don't announce the lock - it's just tracked internally

        # Check for weather-changing moves and stat-changing moves (power 0 indicates non-damaging move)
        if move.power == 0:
            weather_moves = {
                "Rain Dance": Weather.RAIN,
                "Sunny Day": Weather.SUN,
                "Sandstorm": Weather.SANDSTORM,
                "Hail": Weather.HAIL
            }
            if move.name in weather_moves:
                self.set_weather(weather_moves[move.name], turns=5)
                return  # Weather moves don't deal damage

            # Handle stat-changing moves (power 0, has stat_changes)
            if move.stat_changes and not attacker.is_fainted():
                # Determine target
                if move.stat_change_target == "self":
                    target_is_player = is_player
                else:  # "opponent"
                    target_is_player = not is_player

                # Apply each stat change
                target_creature = self.player_active if target_is_player else self.opponent_active
                for stat, stages in move.stat_changes.items():
                    self.stat_manager.modify_stat_stage(target_creature, target_is_player, stat, stages, self.log)
                return  # Stat-changing moves don't deal damage

        # Check accuracy
        if random.randint(1, 100) > move.accuracy:
            self.log.add("The attack missed!")
            return

        # Check for critical hit
        is_critical = self.damage_calculator.check_critical_hit(attacker, defender, move)

        # Handle multi-hit moves
        min_hits, max_hits = move.multi_hit
        num_hits = 1
        if max_hits > 1:
            # Check for Skill Link ability (always hit max times)
            has_skill_link = False
            if attacker.species.ability and attacker.species.ability.name == "Skill Link":
                has_skill_link = True

            if has_skill_link:
                num_hits = max_hits  # Always hit maximum times
            else:
                # Multi-hit moves hit 2-5 times randomly
                num_hits = random.randint(min_hits, max_hits)

        total_damage = 0
        effectiveness = get_effectiveness(move.type, defender.species.types)

        # Execute hits
        for hit_num in range(num_hits):
            if defender.is_fainted():
                break  # Stop if defender faints mid-multi-hit

            # Calculate damage (with critical hit flag)
            # Create stat modifier callables for damage calculator
            is_attacker_player = (attacker == self.player_active)
            is_defender_player = (defender == self.player_active)

            def get_attacker_stat(creature, stat):
                return self.stat_manager.get_modified_stat(creature, stat, is_attacker_player)

            def get_defender_stat(creature, stat):
                return self.stat_manager.get_modified_stat(creature, stat, is_defender_player)

            damage = self.damage_calculator.calculate_damage(
                attacker, defender, move, is_critical, self.weather,
                get_attacker_stat, get_defender_stat
            )

            # Check for Focus Band/Sash before applying damage
            damage = self._apply_focus_item(defender, damage)

            # Apply damage
            actual_damage = defender.take_damage(damage)
            total_damage += actual_damage

            # Show individual hit messages for multi-hit moves
            if num_hits > 1:
                self.log.add(f"Hit {hit_num + 1}! {defender_name} took {actual_damage} damage!")

        # Create final damage message for single-hit or multi-hit summary
        if num_hits == 1:
            damage_message = f"{defender_name} took {total_damage} damage!"

            # Add critical hit indicator first
            if is_critical:
                damage_message += " (Critical hit!)"

            # Add effectiveness indicator to damage message
            if effectiveness > 1.5:
                damage_message += " (Super effective!)"
            elif effectiveness < 0.75:
                damage_message += " (Not very effective...)"

            self.log.add(damage_message)
        else:
            # Multi-hit summary message
            summary_msg = f"Hit {num_hits} time(s)! Total damage: {total_damage}!"
            if effectiveness > 1.5:
                summary_msg += " (Super effective!)"
            elif effectiveness < 0.75:
                summary_msg += " (Not very effective...)"
            self.log.add(summary_msg)

        # Handle recoil damage from move
        if move.recoil_percent > 0 and total_damage > 0:
            recoil_damage = max(1, (total_damage * move.recoil_percent) // 100)

            # Check for Rock Head ability (prevents recoil damage)
            has_rock_head = False
            if attacker.species.ability and attacker.species.ability.name == "Rock Head":
                has_rock_head = True

            if not has_rock_head:
                attacker.take_damage(recoil_damage)
                self.log.add(f"{attacker_name} took {recoil_damage} recoil damage!")

                if attacker.is_fainted():
                    self.log.add(f"{attacker_name} fainted from recoil!")

        # Handle Life Orb recoil (if attacker is still alive and dealt damage)
        if (total_damage > 0 and not attacker.is_fainted() and
            attacker.held_item and attacker.held_item.effect_type == EFFECT_LIFE_ORB):
            life_orb_recoil = max(1, int(attacker.max_hp * 0.10))  # 10% of max HP
            attacker.take_damage(life_orb_recoil)
            self.log.add(f"{attacker_name} was hurt by its Life Orb!")

            if attacker.is_fainted():
                self.log.add(f"{attacker_name} fainted from Life Orb recoil!")

        # Shell Bell healing (if attacker still alive and dealt damage)
        if (total_damage > 0 and not attacker.is_fainted() and
            attacker.held_item and attacker.held_item.effect_type == EFFECT_STAT_HEAL):
            if attacker.held_item.effect_data.get("heal_on_damage"):
                # Shell Bell heals 1/8 of damage dealt
                heal_amount = max(1, int(total_damage * 0.125))
                if attacker.current_hp < attacker.max_hp:
                    attacker.heal(heal_amount)
                    self.log.add(f"{attacker_name} restored HP using Shell Bell!")

        # Rocky Helmet contact damage (if defender still alive and move made contact)
        if (total_damage > 0 and not defender.is_fainted() and not attacker.is_fainted() and
            move.is_contact and defender.held_item and
            defender.held_item.effect_type == EFFECT_CONTACT_DAMAGE):
            # Rocky Helmet deals 1/6 of attacker's max HP
            helmet_damage = max(1, int(attacker.max_hp * defender.held_item.effect_value))
            attacker.take_damage(helmet_damage)
            self.log.add(f"{attacker_name} was hurt by {defender_name}'s Rocky Helmet!")

            if attacker.is_fainted():
                self.log.add(f"{attacker_name} fainted from Rocky Helmet damage!")

        # Try to apply status effect from move (only if defender not fainted)
        if move.status_effect and move.status_chance > 0 and not defender.is_fainted():
            if not defender.has_status():  # Can't inflict status if already has one
                if random.randint(1, 100) <= move.status_chance:
                    defender.apply_status(move.status_effect)
                    status_name = move.status_effect.value.capitalize()
                    self.log.add(f"{defender_name} was afflicted with {status_name}!")

        # Apply stat changes from move
        if move.stat_changes and not attacker.is_fainted():
            # Check if stat changes should apply (chance-based)
            if random.randint(1, 100) <= move.stat_change_chance:
                # Determine target
                if move.stat_change_target == "self":
                    target_is_player = is_player
                else:  # "opponent"
                    target_is_player = not is_player

                # Apply each stat change
                target_creature = self.player_active if target_is_player else self.opponent_active
                for stat, stages in move.stat_changes.items():
                    self.stat_manager.modify_stat_stage(target_creature, target_is_player, stat, stages, self.log)

        # Check if defender fainted
        if defender.is_fainted():
            self.log.add(f"{defender_name} fainted!")

        # Process status damage at end of turn
        self._process_status_damage(attacker, defender)

    def _execute_struggle(
        self,
        attacker: Creature,
        defender: Creature,
        is_player: bool
    ):
        """Execute Struggle move (used when no PP remaining)."""
        attacker_name = attacker.get_display_name()
        defender_name = defender.get_display_name()

        self.log.add(f"{attacker_name} used Struggle!")

        # Struggle always hits and does recoil damage
        damage = max(1, int(attacker.attack * 0.5))
        actual_damage = defender.take_damage(damage)

        self.log.add(f"{defender_name} took {actual_damage} damage!")

        # Recoil damage (25% of max HP)
        recoil = max(1, int(attacker.max_hp * 0.25))
        attacker.take_damage(recoil)
        self.log.add(f"{attacker_name} is hurt by recoil!")

        # Check if either fainted
        if defender.is_fainted():
            self.log.add(f"{defender_name} fainted!")
        if attacker.is_fainted():
            self.log.add(f"{attacker_name} fainted from recoil!")



    def _determine_order(self) -> bool:
        """
        Determine if player goes first based on speed.

        Returns:
            True if player goes first
        """
        # Get modified speed (includes stat stages and ability modifiers)
        player_speed = self.stat_manager.get_modified_stat(self.player_active, "speed", True)
        opponent_speed = self.stat_manager.get_modified_stat(self.opponent_active, "speed", False)

        # Paralysis reduces speed by 75%
        if self.player_active.status == StatusEffect.PARALYSIS:
            player_speed = int(player_speed * 0.25)

        if self.opponent_active.status == StatusEffect.PARALYSIS:
            opponent_speed = int(opponent_speed * 0.25)

        if player_speed > opponent_speed:
            return True
        elif player_speed < opponent_speed:
            return False
        else:
            return random.choice([True, False])

    def _determine_order_with_priority(
        self,
        player_move: Optional[Move],
        opponent_move: Optional[Move]
    ) -> bool:
        """
        Determine if player goes first based on move priority, then speed.
        Also checks for Quick Claw effect.

        Args:
            player_move: The move the player is using
            opponent_move: The move the opponent is using

        Returns:
            True if player goes first
        """
        # Check for Quick Claw (20% chance to move first)
        player_has_quick_claw = (self.player_active.held_item and
                                  self.player_active.held_item.name == "Quick Claw")
        opponent_has_quick_claw = (self.opponent_active.held_item and
                                    self.opponent_active.held_item.name == "Quick Claw")

        # Quick Claw activation (both can't activate in same turn - first one checked wins)
        if player_has_quick_claw and random.random() < 0.20:
            self.log.add(f"{self.player_active.get_display_name()}'s Quick Claw activated!")
            return True

        if opponent_has_quick_claw and random.random() < 0.20:
            self.log.add(f"{self.opponent_active.get_display_name()}'s Quick Claw activated!")
            return False

        player_priority = player_move.priority if player_move else 0
        opponent_priority = opponent_move.priority if opponent_move else 0

        # Higher priority always goes first
        if player_priority > opponent_priority:
            return True
        elif player_priority < opponent_priority:
            return False
        else:
            # Same priority - use speed to determine order
            return self._determine_order()

    def _try_run(self) -> bool:
        """
        Attempt to run from battle.

        Returns:
            True if successfully ran away
        """
        if not self.can_run:
            self.log.add("Can't run from a trainer battle!")
            return False

        # Wild battles: 50% base chance + speed difference
        if self.is_wild:
            chance = 50 + (self.player_active.speed - self.opponent_active.speed)
            chance = max(10, min(100, chance))

            if random.randint(1, 100) <= chance:
                self.log.add("Got away safely!")
                return True
            else:
                self.log.add("Can't escape!")
                self._opponent_turn()  # Opponent gets a free turn
                return False

        return False

    def _switch_creature(self, is_player: bool, index: int):
        """Switch active creature."""
        team = self.player_team if is_player else self.opponent_team

        if 0 <= index < len(team.creatures):
            new_creature = team.creatures[index]
            if not new_creature.is_fainted():
                if is_player:
                    self.player_active = new_creature
                    # Reset player stat stages when switching
                    self.stat_manager.reset_stat_stages(True)
                    # Update ability stat modifiers
                    self.stat_manager.update_ability_stat_modifiers(new_creature, True, self.weather)
                    self.log.add(f"Go, {new_creature.get_display_name()}!")
                    # Trigger on-entry ability
                    self._trigger_on_entry_ability(new_creature, True)
                else:
                    self.opponent_active = new_creature
                    # Reset opponent stat stages when switching
                    self.stat_manager.reset_stat_stages(False)
                    # Update ability stat modifiers
                    self.stat_manager.update_ability_stat_modifiers(new_creature, False, self.weather)
                    self.log.add(f"Opponent sent out {new_creature.get_display_name()}!")
                    # Trigger on-entry ability
                    self._trigger_on_entry_ability(new_creature, False)

    def _check_fainted(self):
        """Check for fainted creatures and prompt for switches."""
        # Check player's active creature
        if self.player_active.is_fainted():
            next_active = self.player_team.get_first_active()
            if next_active:
                self.player_active = next_active
                self.log.add(f"Go, {next_active.get_display_name()}!")

        # Check opponent's active creature
        if self.opponent_active.is_fainted():
            next_active = self.opponent_team.get_first_active()
            if next_active:
                self.opponent_active = next_active
                self.log.add(f"Opponent sent out {next_active.get_display_name()}!")
            # Award experience to player's creature
            if self.player_active and not self.player_active.is_fainted():
                exp_gained = self._calculate_exp_reward()
                self.log.add(f"{self.player_active.get_display_name()} gained {exp_gained} EXP!")
                if self.player_active.gain_exp(exp_gained):
                    self.log.add(f"{self.player_active.get_display_name()} grew to level {self.player_active.level}!")

                    # Check if creature can learn a new move
                    learnable_move = self.player_active.get_learnable_move()
                    if learnable_move:
                        self.log.add(f"{self.player_active.get_display_name()} can learn {learnable_move.name}!")

                    # Check if creature can evolve
                    if self.player_active.can_evolve():
                        self.log.add(f"{self.player_active.get_display_name()} can evolve!")

    def _calculate_exp_reward(self) -> int:
        """Calculate experience reward for defeating opponent."""
        # Simplified: base 50 * opponent level
        if self.opponent_active:
            return 50 * self.opponent_active.level
        return 50

    def _check_battle_end(self):
        """Check if battle has ended."""
        if not self.player_team.has_active_creatures():
            self.result = BattleResult.OPPONENT_WIN
            self.log.add("You lost the battle!")
        elif not self.opponent_team.has_active_creatures():
            self.result = BattleResult.PLAYER_WIN
            self.log.add("You won the battle!")

    def _get_move_by_index(
        self,
        creature: Creature,
        index: int
    ) -> Optional[Move]:
        """Get move by index from creature's personal moves."""
        if 0 <= index < len(creature.moves):
            return creature.moves[index]
        return None

    def _process_status_damage(self, attacker: Creature, defender: Creature):
        """Process status damage for both creatures at end of turn."""
        # Process attacker status
        if attacker.has_status():
            damage = attacker.process_status_damage()
            if damage > 0:
                status_name = attacker.status.value.capitalize()
                self.log.add(f"{attacker.get_display_name()} is hurt by {status_name}! ({damage} damage)")
                if attacker.is_fainted():
                    self.log.add(f"{attacker.get_display_name()} fainted from {status_name}!")

        # Process defender status
        if defender.has_status():
            damage = defender.process_status_damage()
            if damage > 0:
                status_name = defender.status.value.capitalize()
                self.log.add(f"{defender.get_display_name()} is hurt by {status_name}! ({damage} damage)")
                if defender.is_fainted():
                    self.log.add(f"{defender.get_display_name()} fainted from {status_name}!")

    def try_capture(self, ball_strength: float = 1.0) -> bool:
        """
        Attempt to capture opponent creature (wild battles only).

        Args:
            ball_strength: Multiplier for capture rate (1.0 = standard ball)

        Returns:
            True if capture successful
        """
        if not self.is_wild:
            self.log.add("Can't capture trainer's creatures!")
            return False

        if self.opponent_active.is_fainted():
            self.log.add("Can't capture a fainted creature!")
            return False

        # Capture formula (simplified)
        # Lower HP = higher catch rate
        hp_factor = 1 - (self.opponent_active.current_hp / self.opponent_active.max_hp)
        catch_rate = (hp_factor * 50 + 10) * ball_strength

        if random.uniform(0, 100) < catch_rate:
            self.log.add(f"Captured {self.opponent_active.species.name}!")
            self.result = BattleResult.CAPTURED
            return True
        else:
            self.log.add("The creature broke free!")
            self._opponent_turn()  # Opponent gets a turn
            self._check_fainted()
            self._check_battle_end()
            return False

    def _process_weather(self):
        """Process weather effects and end-of-turn held item effects."""
        # Process weather damage
        if self.weather != Weather.NONE:
            # Sandstorm damages non-Terra/Metal/Beast creatures
            if self.weather == Weather.SANDSTORM:
                self._process_sandstorm_damage(self.player_active, "player")
                self._process_sandstorm_damage(self.opponent_active, "opponent")

            # Hail damages non-Frost creatures
            elif self.weather == Weather.HAIL:
                self._process_hail_damage(self.player_active, "player")
                self._process_hail_damage(self.opponent_active, "opponent")

            # Decrement weather duration if it has a limit
            if self.weather_turns > 0:
                self.weather_turns -= 1
                if self.weather_turns == 0:
                    weather_name = self.weather.value.capitalize()
                    self.log.add(f"The {weather_name} subsided.")
                    self.weather = Weather.NONE

        # Process end-of-turn held item effects (Leftovers, etc.)
        self._process_held_item_effects(self.player_active)
        self._process_held_item_effects(self.opponent_active)

    def _process_sandstorm_damage(self, creature: Creature, side: str):
        """Process sandstorm damage for a creature."""
        if creature.is_fainted():
            return

        # Sandstorm doesn't damage Terra, Metal, or Beast types
        immune_types = ["Terra", "Metal", "Beast"]
        if any(t in immune_types for t in creature.species.types):
            return

        damage = max(1, int(creature.max_hp / 16))  # 1/16 max HP
        creature.take_damage(damage)
        self.log.add(f"{creature.get_display_name()} is buffeted by the sandstorm! ({damage} damage)")

        if creature.is_fainted():
            self.log.add(f"{creature.get_display_name()} fainted from the sandstorm!")

    def _process_hail_damage(self, creature: Creature, side: str):
        """Process hail damage for a creature."""
        if creature.is_fainted():
            return

        # Hail doesn't damage Frost types
        if "Frost" in creature.species.types:
            return

        damage = max(1, int(creature.max_hp / 16))  # 1/16 max HP
        creature.take_damage(damage)
        self.log.add(f"{creature.get_display_name()} is pelted by hail! ({damage} damage)")

        if creature.is_fainted():
            self.log.add(f"{creature.get_display_name()} fainted from the hail!")

    def _apply_focus_item(self, creature: Creature, damage: int) -> int:
        """
        Check if Focus Band/Sash prevents fainting and adjust damage accordingly.
        Returns the adjusted damage amount.

        Args:
            creature: The creature taking damage
            damage: The damage that would be dealt

        Returns:
            Adjusted damage (reduced to leave 1 HP if Focus item triggers)
        """
        if not creature.held_item or creature.held_item.effect_type != EFFECT_FOCUS_BAND:
            return damage

        # Only trigger if damage would be fatal
        if damage < creature.current_hp:
            return damage

        item = creature.held_item
        name = creature.get_display_name()

        # Focus Sash - guaranteed survival if at full HP (one-time use)
        if item.name == "Focus Sash":
            if creature.current_hp == creature.max_hp and not creature.focus_sash_used:
                creature.focus_sash_used = True
                self.log.add(f"{name} held on using its Focus Sash!")
                return creature.current_hp - 1  # Leave at 1 HP

        # Focus Band - 10% chance to survive
        elif item.name == "Focus Band":
            if random.random() < 0.10:  # 10% chance
                self.log.add(f"{name} held on using its Focus Band!")
                return creature.current_hp - 1  # Leave at 1 HP

        return damage

    def _process_held_item_effects(self, creature: Creature):
        """Process end-of-turn held item effects (Leftovers, Flame Orb, etc.)."""
        if creature.is_fainted() or not creature.held_item:
            return

        item = creature.held_item
        name = creature.get_display_name()

        # Leftovers - restores 1/16 max HP each turn
        if item.effect_type == EFFECT_STAT_HEAL and not item.effect_data.get("heal_on_damage"):
            if creature.current_hp < creature.max_hp:
                heal_amount = max(1, int(creature.max_hp * item.effect_value))
                creature.heal(heal_amount)
                self.log.add(f"{name} restored some HP using {item.name}!")

        # Flame Orb / Toxic Orb - auto-inflict status at end of turn
        if item.effect_type == EFFECT_AUTO_STATUS:
            if not creature.has_status():  # Only if not already statused
                status_name = item.effect_data.get("status", "")
                if status_name == "burn":
                    creature.apply_status(StatusEffect.BURN)
                    self.log.add(f"{name} was burned by its {item.name}!")
                elif status_name == "poison":
                    creature.apply_status(StatusEffect.POISON)
                    self.log.add(f"{name} was poisoned by its {item.name}!")

    def set_weather(self, weather: Weather, turns: int = 5):
        """
        Set the current weather condition.

        Args:
            weather: Weather condition to set
            turns: Number of turns weather lasts (0 = infinite)
        """
        old_weather = self.weather
        self.weather = weather
        self.weather_turns = turns

        if weather != Weather.NONE:
            weather_name = weather.value.capitalize()
            if old_weather == Weather.NONE:
                self.log.add(f"{weather_name} started!")
            else:
                self.log.add(f"The weather changed to {weather_name}!")

    def _trigger_on_entry_ability(self, creature: Creature, is_player: bool):
        """
        Trigger abilities that activate when a creature enters battle.

        Args:
            creature: The creature entering battle
            is_player: True if this is the player's creature
        """
        if not creature:
            return

        ability = creature.species.ability
        if not ability:
            return

        creature_name = creature.get_display_name()

        # Weather-summoning abilities
        if ability.effect_type == "weather_sun":
            self.set_weather(Weather.SUN, turns=5)
            self.log.add(f"{creature_name}'s {ability.name} made it sunny!")
        elif ability.effect_type == "weather_rain":
            self.set_weather(Weather.RAIN, turns=5)
            self.log.add(f"{creature_name}'s {ability.name} made it rain!")
        elif ability.effect_type == "weather_sandstorm":
            self.set_weather(Weather.SANDSTORM, turns=5)
            self.log.add(f"{creature_name}'s {ability.name} whipped up a sandstorm!")

        # Intimidate - lowers opponent's Attack on entry
        elif ability.effect_type == "lower_attack_entry":
            target_creature = self.opponent_active if is_player else self.player_active
            target_is_player = not is_player
            # Lower attack by 1 stage
            self.stat_manager.modify_stat_stage(target_creature, target_is_player, "attack", -1, self.log)
            if is_player:
                self.log.add(f"{creature_name}'s {ability.name} lowered the foe's Attack!")
            else:
                self.log.add(f"The opposing {creature_name}'s {ability.name} lowered your Attack!")


