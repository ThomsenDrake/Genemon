"""
Battle engine with turn-based combat mechanics.
"""

import random
from typing import Optional, List, Tuple
from enum import Enum
from ..core.creature import Creature, Move, Team, StatusEffect
from ..creatures.types import get_effectiveness


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

        self.player_active = player_team.get_first_active()
        self.opponent_active = opponent_team.get_first_active()

        self.log = BattleLog()
        self.result = BattleResult.ONGOING
        self.turn_count = 0

        # Battle start message
        if is_wild:
            self.log.add(f"A wild {self.opponent_active.species.name} appeared!")
        else:
            self.log.add("Battle started!")

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
                # Determine order based on speed
                player_first = self._determine_order()

                if player_first:
                    self._execute_attack(
                        self.player_active,
                        self.opponent_active,
                        player_move,
                        is_player=True
                    )
                    if not self.opponent_active.is_fainted():
                        self._opponent_turn()
                else:
                    self._opponent_turn()
                    if not self.player_active.is_fainted():
                        self._execute_attack(
                            self.player_active,
                            self.opponent_active,
                            player_move,
                            is_player=True
                        )

        # Check for fainted creatures
        self._check_fainted()

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

        # Check accuracy
        if random.randint(1, 100) > move.accuracy:
            self.log.add("The attack missed!")
            return

        # Calculate damage
        damage = self._calculate_damage(attacker, defender, move)

        # Apply damage
        actual_damage = defender.take_damage(damage)

        self.log.add(f"{defender_name} took {actual_damage} damage!")

        # Check for effectiveness message
        effectiveness = get_effectiveness(move.type, defender.species.types)
        if effectiveness > 1.5:
            self.log.add("It's super effective!")
        elif effectiveness < 0.75:
            self.log.add("It's not very effective...")

        # Try to apply status effect from move (only if defender not fainted)
        if move.status_effect and move.status_chance > 0 and not defender.is_fainted():
            if not defender.has_status():  # Can't inflict status if already has one
                if random.randint(1, 100) <= move.status_chance:
                    defender.apply_status(move.status_effect)
                    status_name = move.status_effect.value.capitalize()
                    self.log.add(f"{defender_name} was afflicted with {status_name}!")

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

    def _calculate_damage(
        self,
        attacker: Creature,
        defender: Creature,
        move: Move
    ) -> int:
        """
        Calculate damage for an attack (simplified Gen 1 formula).

        Args:
            attacker: Attacking creature
            defender: Defending creature
            move: Move being used

        Returns:
            Damage amount
        """
        # Base damage calculation
        level = attacker.level
        attack_stat = attacker.attack
        defense_stat = defender.defense
        power = move.power

        # Base damage formula (simplified)
        damage = ((2 * level / 5 + 2) * power * attack_stat / defense_stat / 50) + 2

        # Type effectiveness
        effectiveness = get_effectiveness(move.type, defender.species.types)
        damage *= effectiveness

        # STAB (Same Type Attack Bonus)
        if move.type in attacker.species.types:
            damage *= 1.5

        # Random factor (85-100%)
        damage *= random.uniform(0.85, 1.0)

        return max(1, int(damage))

    def _determine_order(self) -> bool:
        """
        Determine if player goes first based on speed.

        Returns:
            True if player goes first
        """
        if self.player_active.speed > self.opponent_active.speed:
            return True
        elif self.player_active.speed < self.opponent_active.speed:
            return False
        else:
            return random.choice([True, False])

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
                    self.log.add(f"Go, {new_creature.get_display_name()}!")
                else:
                    self.opponent_active = new_creature
                    self.log.add(f"Opponent sent out {new_creature.get_display_name()}!")

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
