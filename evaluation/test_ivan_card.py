from __future__ import annotations
import argparse
import os
from typing import Callable

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from game import GameState
from battle import BattleState
from config import Character, Verbose
from card import Card, CardRepo, CardType, Rarity
from value import ConstValue
from action.agent_targeted_action import ApplyStatus
from target.agent_target import SelfAgentTarget
from status_effecs import StatusEffectRepo
from ggpa.random_bot import RandomBot
from ggpa.backtrack import BacktrackBot
from ggpa.ggpa import GGPA


def make_ivan_card() -> Card:
    """
    Return Ivan's card. Modify this function to change the tested effect.
    Current effect: 1-cost Skill that applies 1 Vigor to the player (self).
    """
    return Card(
        "IvanCard",
        CardType.SKILL,
        ConstValue(1),
        Character.IRON_CLAD,
        Rarity.UNCOMMON,
        ApplyStatus(ConstValue(1), StatusEffectRepo.VIGOR).To(SelfAgentTarget())
    )


def simulate_one(i: int, bot: GGPA, new_card_factory: Callable[[], Card], enemies: str) -> tuple[str, int, bool]:
    card = new_card_factory()
    game_state = GameState(Character.IRON_CLAD, bot, 0)
    # start from starter/basic deck and add Ivan's card
    base = CardRepo.get_basics()
    game_state.set_deck(*base)
    game_state.add_to_deck(card)

    # use a simple enemy (JawWorm by default)
    from agent import JawWorm
    battle_state = BattleState(game_state, JawWorm(game_state), verbose=Verbose.NO_LOG)
    battle_state.run()
    return (bot.name, game_state.player.health, game_state.get_end_results() != -1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=int, default=100, help='Number of simulated games')
    parser.add_argument('--bot', type=str, default='random', help='Agent to use: random or bt{depth} (e.g., bt3)')
    parser.add_argument('--enemies', type=str, default='j', help='Enemies string, e.g. j for JawWorm')
    args = parser.parse_args()

    runs = args.runs
    bot_name = args.bot

    if bot_name == 'random':
        bot = RandomBot()
    elif bot_name.startswith('bt'):
        depth = int(bot_name[2:]) if len(bot_name) > 2 else 3
        bot = BacktrackBot(depth, False)
    else:
        bot = RandomBot()

    print(f'Running {runs} simulations with bot {bot.name} and Ivan card...')
    results = [simulate_one(i, bot, make_ivan_card, args.enemies) for i in range(runs)]
    wins = sum(1 for _, _, win in results if win)
    avg_hp = sum(hp for _, hp, _ in results) / len(results)
    print(f'Wins: {wins}/{runs} ({wins/runs:.2%}), avg final HP: {avg_hp:.2f}')


if __name__ == '__main__':
    main()
