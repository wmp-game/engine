from threading import Thread
import random
import time
import copy
import os

from .battle_components import Battle
from .util import Logger


class Engine:
    def __init__(self):
        self.battle_time = 100.0
        self.timefreeze = 0.1
        self.burning_dot = 0.5

    def melee_effect(self, d):
        return round(-32.0 * (d - 0.2) * (d - 1.0), 2)

    def long_ranged_magic_effect(self, d):
        return round(-3.0 * (d - 3.0) * (d - 5.0), 2)

    def short_ranged_magic_effect(self, d):
        return round(-(d - 3.0) * (d + 3.0) / 2, 2)

    def timer(self):
        return max(0.0, round(self.battle_time - (time.time() - self.starting_time) / self.timefreeze, 2))

    def battle_is_on(self):
        if (self.timer() == 0.0):
            return False
        if (self.team_a_data['warrior']['hp'] == 0.0
            and self.team_a_data['mage']['hp'] == 0.0
                and self.team_a_data['priest']['hp'] == 0.0):
            return False
        if (self.team_b_data['warrior']['hp'] == 0.0
            and self.team_b_data['mage']['hp'] == 0.0
                and self.team_b_data['priest']['hp'] == 0.0):
            return False
        return not self.INTERRUPTED

    def resolve_wait_action(self, this_team_data, unit, target):
        if (target >= 0.01 and target <= 1.0):
            self.logger.feed('{}|{}|{}|wait|{}'.format(
                self.timer(), this_team_data['name'], unit, round(target, 2)))
            time.sleep(target * self.timefreeze)
        else:
            time.sleep(self.timefreeze)

    def is_in_range(self, action, d):
        if (action == 'move'):
            return (0.009 <= d and d <= 1.001)
        elif (action == 'hit'):
            return (0.199 <= d and d <= 1.001)
        elif (action == 'bash'):
            return (0.199 <= d and d <= 1.001)
        elif (action == 'burn'):
            return (2.999 <= d and d <= 5.001)
        elif (action == 'freeze'):
            return (d <= 3.001)
        elif (action == 'heal'):
            return (d <= 3.001)
        elif (action == 'silence'):
            return (2.999 <= d and d <= 5.001)

    def resolve_move_action(self, this_team_data, unit, target):
        x_orig = this_team_data[unit]['pos'][0]
        y_orig = this_team_data[unit]['pos'][1]
        x_dest = target[0]
        y_dest = target[1]
        d = ((y_dest - y_orig)**2 + (x_dest - x_orig)**2)**(1 / 2)
        if (not self.is_in_range('move', d) or x_dest < 0.0 or x_dest > 30.0 or y_dest < 0.0 or y_dest > 30.0):
            time.sleep(self.timefreeze)
            return
        if (this_team_data[unit]['sts']['freezing'] > 0.0):
            x_dest = (x_orig + x_dest) / 2
            y_dest = (y_orig + y_dest) / 2

        this_team_data[unit]['pos'] = (x_dest, y_dest)
        self.logger.feed('{}|{}|{}|move|{},{}|{},{}'
                         .format(self.timer(), this_team_data['name'], unit,
                                 round(x_orig, 2), round(y_orig, 2), round(x_dest, 2), round(y_dest, 2)))
        time.sleep(max(d * self.timefreeze, 0.1 * self.timefreeze))

    def distance_between_units(self, this_team_data, other_team_data, this_unit, other_unit):
        this_x = this_team_data[this_unit]['pos'][0]
        this_y = this_team_data[this_unit]['pos'][1]
        other_x = other_team_data[other_unit]['pos'][0]
        other_y = other_team_data[other_unit]['pos'][1]
        return ((other_y - this_y)**2 + (other_x - this_x)**2)**(1 / 2)

    def resolve_hit_action(self, this_team_data, other_team_data, target):
        d = self.distance_between_units(
            this_team_data, other_team_data, 'warrior', target)
        if (self.is_in_range('hit', d)
                and other_team_data[target]['hp'] > 0.0):
            effect = self.melee_effect(d)
            other_team_data[target]['hp'] -= effect
            self.logger.feed('{}|{}|warrior|hit|{}|{}'
                             .format(self.timer(), this_team_data['name'], target, effect))
            if (other_team_data[target]['hp'] <= 0.0):
                other_team_data[target]['hp'] = 0.0
                self.logger.feed(
                    '{}|{}|{}|die'.format(self.timer(), other_team_data['name'], target))
        time.sleep(self.timefreeze)

    def resolve_bash_action(self, this_team_data, other_team_data, target):
        d = self.distance_between_units(
            this_team_data, other_team_data, 'warrior', target)
        if (self.is_in_range('bash', d)
                and other_team_data[target]['hp'] > 0.0
                and this_team_data['warrior']['sts']['silenced'] == 0.0
                and this_team_data['warrior']['cds']['bash'] == 0.0):
            effect = self.melee_effect(d)
            other_team_data[target]['sts']['stun'] = effect
            this_team_data['warrior']['cds']['bash'] = 2*effect
            self.logger.feed('{}|{}|warrior|stun|{}|{}'
                             .format(self.timer(), this_team_data['name'], target, effect))
            self.logger.feed('{}|{}|warrior|+cd|bash|{}'
                             .format(self.timer(), this_team_data['name'], 2*effect))
            self.logger.feed('{}|{}|{}|+sts|stun|{}'
                             .format(self.timer(), other_team_data['name'], target, effect))
        time.sleep(self.timefreeze)

    def resolve_warrior_action(self, this_team_data, other_team_data, command):
        action, target = command

        if (action == 'wait'):
            self.resolve_wait_action(this_team_data, 'warrior', target)
            return

        if (action == 'move'):
            self.resolve_move_action(this_team_data, 'warrior', target)
            return
        elif (action == 'hit'):
            self.resolve_hit_action(this_team_data, other_team_data, target)
            return
        elif (action == 'bash'):
            self.resolve_bash_action(this_team_data, other_team_data, target)
            return
        else:
            time.sleep(self.timefreeze)

    def resolve_burn_action(self, this_team_data, other_team_data, target):
        d = self.distance_between_units(
            this_team_data, other_team_data, 'mage', target)
        if (self.is_in_range('burn', d)
                and this_team_data['mage']['sts']['silenced'] == 0.0
                and other_team_data[target]['hp'] > 0.0):
            effect = self.long_ranged_magic_effect(d)
            other_team_data[target]['hp'] -= effect
            self.logger.feed('{}|{}|mage|burn|{}|{}'
                             .format(self.timer(), this_team_data['name'], target, effect))
            if (other_team_data[target]['sts']['freezing'] > 0.0):
                other_team_data[target]['sts']['freezing'] = 0.0
                self.logger.feed('{}|{}|{}|-sts|freezing'
                                 .format(self.timer(), other_team_data['name'], target))
            other_team_data[target]['sts']['burning'] = 2*effect
            self.logger.feed('{}|{}|{}|+sts|burning|{}'
                             .format(self.timer(), other_team_data['name'], target, 2*effect))
            if (other_team_data[target]['hp'] <= 0.0):
                other_team_data[target]['hp'] = 0.0
                self.logger.feed(
                    '{}|{}|{}|die'.format(self.timer(), other_team_data['name'], target))
        time.sleep(self.timefreeze)

    def resolve_freeze_action(self, this_team_data, other_team_data, target):
        d = self.distance_between_units(
            this_team_data, other_team_data, 'mage', target)
        if (self.is_in_range('freeze', d)
                and this_team_data['mage']['sts']['silenced'] == 0.0
                and other_team_data[target]['hp'] > 0.0):
            effect = self.short_ranged_magic_effect(d)
            other_team_data[target]['hp'] -= effect/2
            self.logger.feed('{}|{}|mage|freeze|{}|{}'
                             .format(self.timer(), this_team_data['name'], target, effect/2))
            if (other_team_data[target]['sts']['burning'] > 0.0):
                other_team_data[target]['sts']['burning'] = 0.0
                self.logger.feed('{}|{}|{}|-sts|burning'
                                 .format(self.timer(), other_team_data['name'], target))
            other_team_data[target]['sts']['freezing'] = 2*effect
            self.logger.feed('{}|{}|{}|+sts|freezing|{}'
                             .format(self.timer(), other_team_data['name'], target, 2*effect))
            if (other_team_data[target]['hp'] <= 0.0):
                other_team_data[target]['hp'] = 0.0
                self.logger.feed(
                    '{}|{}|{}|die'.format(self.timer(), other_team_data['name'], target))
        time.sleep(self.timefreeze)

    def resolve_mage_action(self, this_team_data, other_team_data, command):
        action, target = command

        if (action == 'wait'):
            self.resolve_wait_action(this_team_data, 'mage', target)
            return

        if (action == 'move'):
            self.resolve_move_action(this_team_data, 'mage', target)
            return
        elif (action == 'burn'):
            self.resolve_burn_action(this_team_data, other_team_data, target)
            return
        elif (action == 'freeze'):
            self.resolve_freeze_action(this_team_data, other_team_data, target)
            return
        else:
            time.sleep(self.timefreeze)

    def resolve_heal_action(self, this_team_data, other_team_data, target):
        d = self.distance_between_units(
            this_team_data, other_team_data, 'priest', target)
        if (self.is_in_range('heal', d)
                and this_team_data[target]['hp'] > 0.0
                and this_team_data['priest']['sts']['silenced'] == 0.0):
            effect = self.short_ranged_magic_effect(d)
            this_team_data[target]['hp'] += effect
            if (this_team_data[target]['hp'] > 100.0):
                this_team_data[target]['hp'] = 100.0
            self.logger.feed('{}|{}|priest|heal|{}|{}'
                             .format(self.timer(), this_team_data['name'], target, effect))
            for status in ['burning', 'freezing']:
                if (this_team_data[target]['sts'][status] > 0.0):
                    this_team_data[target]['sts'][status] = 0.0
                    self.logger.feed('{}|{}|{}|-sts|{}'
                                     .format(self.timer(), this_team_data['name'], target, status))
        time.sleep(self.timefreeze)

    def resolve_silence_action(self, this_team_data, other_team_data, target):
        d = self.distance_between_units(
            this_team_data, other_team_data, 'priest', target)
        if (self.is_in_range('silence', d)
                and other_team_data[target]['hp'] > 0.0
                and this_team_data['priest']['cds']['silence'] == 0.0
                and this_team_data['priest']['sts']['silenced'] == 0.0):
            effect = self.long_ranged_magic_effect(d)
            other_team_data[target]['sts']['silenced'] = effect
            this_team_data['priest']['cds']['silence'] = 2*effect
            self.logger.feed('{}|{}|priest|silence|{}|{}'
                             .format(self.timer(), this_team_data['name'], target, effect))
            self.logger.feed('{}|{}|priest|+cd|silence|{}'
                             .format(self.timer(), this_team_data['name'], 2*effect))
            self.logger.feed('{}|{}|{}|+sts|silenced|{}'
                             .format(self.timer(), other_team_data['name'], target, effect))
        time.sleep(self.timefreeze)

    def resolve_priest_action(self, this_team_data, other_team_data, command):
        action, target = command

        if (action == 'wait'):
            self.resolve_wait_action(this_team_data, 'priest', target)
            return

        if (action == 'move'):
            self.resolve_move_action(this_team_data, 'priest', target)
            return
        elif (action == 'heal'):
            self.resolve_heal_action(this_team_data, other_team_data, target)
            return
        elif (action == 'silence'):
            self.resolve_silence_action(
                this_team_data, other_team_data, target)
            return
        else:
            time.sleep(self.timefreeze)

    def exec_unit(self, this_team, unit):
        this_team_data = None
        other_team_data = None
        if (this_team == self.team_a):
            this_team_data = self.team_a_data
            other_team_data = self.team_b_data
        else:
            this_team_data = self.team_b_data
            other_team_data = self.team_a_data
        executor = None
        resolver = None
        if (unit == 'warrior'):
            executor = this_team.warrior
            resolver = self.resolve_warrior_action
        elif (unit == 'mage'):
            executor = this_team.mage
            resolver = self.resolve_mage_action
        else:
            executor = this_team.priest
            resolver = self.resolve_priest_action
        battle = Battle(unit)
        while (self.battle_is_on()):
            if (this_team_data[unit]['hp'] <= 0.0):
                time.sleep((self.timer() + 1.0) * self.timefreeze)
            else:
                # try:
                #     battle.update(this_team_data,
                #                   other_team_data, self.timer())
                #     self.thread_tracker[(
                #         this_team_data['name'], unit)] = time.time()
                #     stun = this_team_data[unit]['sts']['stun']
                #     if (stun == 0.0):
                #         resolver(this_team_data, other_team_data,
                #                  executor(battle))
                #     else:
                #         time.sleep(
                #             min(self.timefreeze, stun * self.timefreeze))
                # except Exception:
                #     self.logger.feed('{}|{}|{}|error'.format(
                #         self.timer(), this_team_data['name'], unit))
                #     time.sleep(self.timefreeze)

                battle.update(this_team_data,
                              other_team_data, self.timer())
                self.thread_tracker[(
                    this_team_data['name'], unit)] = time.time()
                stun = this_team_data[unit]['sts']['stun']
                if (stun == 0.0):
                    resolver(this_team_data, other_team_data,
                             executor(battle))
                else:
                    time.sleep(
                        min(self.timefreeze, stun * self.timefreeze))

    def residual_ticker(self, duration, team_data, unit, kind, key):
        time.sleep(duration * self.timefreeze)
        team_data[unit][kind][key] = 0.0
        self.logger.feed(
            '{}|{}|{}|-{}|{}'.format(self.timer(), team_data['name'], unit, kind, key))

    def ticker(self):
        time.sleep(self.timefreeze)
        team_datas = [self.team_a_data, self.team_b_data]
        units = ['warrior', 'mage', 'priest']
        while (self.battle_is_on()):
            random.shuffle(team_datas)
            random.shuffle(units)
            for team_data in team_datas:
                for unit in units:
                    for status in team_data[unit]['sts']:
                        if (team_data[unit]['sts'][status] > 0.0):
                            if (status == 'burning' and team_data[unit]['hp'] > 0.0):
                                team_data[unit]['hp'] -= self.burning_dot
                                self.logger.feed('{}|{}|{}|-hp|{}'
                                                 .format(self.timer(), team_data['name'], unit, self.burning_dot))
                                if (team_data[unit]['hp'] < 0.0):
                                    team_data[unit]['hp'] = 0.0
                                if (team_data[unit]['hp'] == 0.0):
                                    self.logger.feed(
                                        '{}|{}|{}|die'.format(self.timer(), team_data['name'], unit))
                            team_data[unit]['sts'][status] -= 1.0
                            duration = team_data[unit]['sts'][status]
                            if (0.0 < duration < 1.0):
                                Thread(target=self.residual_ticker, args=(
                                    duration, team_data, unit, 'sts', status)).start()
                            elif (team_data[unit]['sts'][status] < 0.0):
                                team_data[unit]['sts'][status] = 0.0
                                self.logger.feed(
                                    '{}|{}|{}|-sts|{}'.format(self.timer(), team_data['name'], unit, status))
                    for skill in team_data[unit]['cds']:
                        if (team_data[unit]['cds'][skill] > 0.0):
                            team_data[unit]['cds'][skill] -= 1.0
                            duration = team_data[unit]['cds'][skill]
                            if (0.0 < duration < 1.0):
                                Thread(target=self.residual_ticker, args=(
                                    duration, team_data, unit, 'cds', skill)).start()
                            elif (duration < 0.0):
                                team_data[unit]['cds'][skill] = 0.0
                                self.logger.feed(
                                    '{}|{}|{}|-cd|{}'.format(self.timer(), team_data['name'], unit, skill))
            time.sleep(self.timefreeze)

    def log_initial_positions(self):
        for team_data in [self.team_a_data, self.team_b_data]:
            for unit in ['warrior', 'mage', 'priest']:
                pos = team_data[unit]['pos']
                x = pos[0]
                y = pos[1]
                self.logger.feed(
                    '{}|{}|{}|start|{},{}'.format(self.timer(), team_data['name'], unit, x, y))

    def is_alive(self, key):
        team_name, unit = key
        team_data = None
        if (team_name == self.team_a.name):
            team_data = self.team_a_data
        else:
            team_data = self.team_b_data
        return team_data[unit]['hp'] > 0.0

    def tldr_scanner(self):
        while (self.battle_is_on()):
            for key in self.thread_tracker:
                tim = time.time()
                if (tim - self.thread_tracker[key] > 2 * self.timefreeze and self.is_alive(key)):
                    self.violator = key[0]
                    self.INTERRUPTED = True
                    break
            time.sleep(self.timefreeze)

    def start_threads(self):
        random.seed(int(round(time.time() * 1000)))
        runs = [(self.team_a, 'warrior'),
                (self.team_a, 'mage'),
                (self.team_a, 'priest'),
                (self.team_b, 'warrior'),
                (self.team_b, 'mage'),
                (self.team_b, 'priest')]
        random.shuffle(runs)
        self.log_initial_positions()
        Thread(target=self.ticker).start()
        for this_team, unit in runs:
            thread = Thread(target=self.exec_unit, args=(this_team, unit))
            thread.daemon = True
            thread.start()
        Thread(target=self.tldr_scanner).start()

    def set_teams(self, team_a, team_b):
        self.team_a = team_a
        self.team_b = team_b
        self.team_a_data = {'name': team_a.name,
                            'warrior': {'pos': (13., 10.), 'hp': 100.,
                                        'sts': {'stun': 0., 'freezing': 0., 'burning': 0., 'silenced': 0.},
                                        'cds': {'bash': 0.}},
                            'mage': {'pos': (15., 10.), 'hp': 100.,
                                     'sts': {'stun': 0., 'freezing': 0., 'burning': 0., 'silenced': 0.},
                                     'cds': {}},
                            'priest': {'pos': (17., 10.), 'hp': 100.,
                                       'sts': {'stun': 0., 'freezing': 0., 'burning': 0., 'silenced': 0.},
                                       'cds': {'silence': 0.}}}
        self.team_b_data = {'name': team_b.name,
                            'warrior': {'pos': (13., 20.), 'hp': 100.,
                                        'sts': {'stun': 0., 'freezing': 0., 'burning': 0., 'silenced': 0.},
                                        'cds': {'bash': 0.}},
                            'mage': {'pos': (15., 20.), 'hp': 100.,
                                     'sts': {'stun': 0., 'freezing': 0., 'burning': 0., 'silenced': 0.},
                                     'cds': {}},
                            'priest': {'pos': (17., 20.), 'hp': 100.,
                                       'sts': {'stun': 0., 'freezing': 0., 'burning': 0., 'silenced': 0.},
                                       'cds': {'silence': 0.}}}

    def start_battle(self, team_a, team_b, log_file=None):
        self.set_teams(team_a, team_b)
        if (log_file is None or log_file == ''):
            log_file = 'battle.log'
        self.logger = Logger()
        self.starting_time = time.time()
        self.INTERRUPTED = False
        self.thread_tracker = {}
        self.violator = None

        Thread(target=self.start_threads).start()

        while (self.battle_is_on()):
            try:
                time.sleep(self.timefreeze)
            except Exception:
                self.INTERRUPTED = True

        chosen = 0

        if (self.INTERRUPTED):
            if (not self.violator is None):
                if (self.violator == self.team_a.name):
                    chosen = 1
                else:
                    chosen = -1
        else:
            sum_team_a = self.team_a_data['warrior']['hp'] + \
                self.team_a_data['mage']['hp'] + \
                self.team_a_data['priest']['hp']
            sum_team_b = self.team_b_data['warrior']['hp'] + \
                self.team_b_data['mage']['hp'] + \
                self.team_b_data['priest']['hp']

            if (sum_team_a > sum_team_b):
                self.logger.feed('winner|{}'.format(self.team_a.name))
                chosen = 1
            elif (sum_team_a < sum_team_b):
                self.logger.feed('winner|{}'.format(self.team_b.name))
                chosen = -1
            else:
                self.logger.feed('draw')

            directory = 'battle_logs/'
            if not os.path.exists(directory):
                os.makedirs(directory)
            self.logger.dump(directory + log_file)

        return (not self.INTERRUPTED, chosen)
