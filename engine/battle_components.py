import random
import time

from .util import d


__all__ = ['Battle']


class Sts:
    def update(self, sts_data):
        self.burning = sts_data['burning']
        self.freezing = sts_data['freezing']
        self.stun = sts_data['stun']
        self.silenced = sts_data['silenced']

class Cds:
    def update(self, cds_data):
        if 'bash' in cds_data:
            self.bash = cds_data['bash']
        if 'silence' in cds_data:
            self.silence = cds_data['silence']


class Unit:
    def __init__(self, name):
        self.name = name
        self.sts = Sts()
        self.cds = Cds()

    def update(self, unit_data):
        self.pos = unit_data['pos']
        self.hp = unit_data['hp']
        self.sts.update(unit_data['sts'])
        self.cds.update(unit_data['cds'])

    def wait(self, duration):
        return ('wait', duration)

    def attempt_spacing(self, target, ideal_distance):
        p1 = self.pos
        if (isinstance(target, tuple)):
            p2 = target
        else:
            p2 = target.pos
        distance = d(p1, p2)
        if (distance == ideal_distance):
            return self.wait(0.01)
        elif (distance == 0.0):
            while (True):
                rand_v_x = random.random() - 0.5
                rand_v_y = random.random() - 0.5
                while (rand_v_x == 0.0 and rand_v_y == 0.0):
                    rand_v_x = random.random() - 0.5
                    rand_v_y = random.random() - 0.5
                rand_magnitude = d(
                    p2, (p2[0] + rand_v_x, p2[1] + rand_v_y))
                x_goal = p2[0] + ideal_distance * \
                    (rand_v_x) / rand_magnitude
                y_goal = p2[1] + ideal_distance * \
                    (rand_v_y) / rand_magnitude
                if (0.0 <= x_goal and x_goal <= 30.0 and 0.0 <= y_goal and y_goal <= 30.0):
                    break
        elif (ideal_distance != 0.0):
            x_goal = p2[0] + ideal_distance * \
                (p1[0] - p2[0]) / distance
            y_goal = p2[1] + ideal_distance * \
                (p1[1] - p2[1]) / distance
            magnitude = d(p1, (x_goal, y_goal))
        else:
            x_goal, y_goal = p2
            magnitude = distance
        try:
            x_dest = p1[0] + min(1.0, magnitude) * \
                (x_goal - p1[0]) / magnitude
            y_dest = p1[1] + min(1.0, magnitude) * \
                (y_goal - p1[1]) / magnitude
            if (0.0 <= x_dest and x_dest <= 30.0 and 0.0 <= y_dest and y_dest <= 30.0):
                return ('move', (x_dest, y_dest))
            else:
                return self.wait(0.01)
        except:
            return self.wait(0.01)

    def move_to(self, target):
        return self.attempt_spacing(target=target, ideal_distance=0.0)

    def hit(self, unit):
        return ('hit', unit.name)

    def bash(self, unit):
        return ('bash', unit.name)

    def burn(self, unit):
        return ('burn', unit.name)

    def freeze(self, unit):
        return ('freeze', unit.name)

    def heal(self, unit):
        return ('heal', unit.name)

    def silence(self, unit):
        return ('silence', unit.name)

    def distance_to(self, target):
        if (isinstance(target, tuple)):
            return d(self.pos, target)
        return d(self.pos, target.pos)


class Team:
    def __init__(self):
        self.warrior = Unit('warrior')
        self.mage = Unit('mage')
        self.priest = Unit('priest')

    def update(self, team_data):
        self.warrior.update(team_data['warrior'])
        self.mage.update(team_data['mage'])
        self.priest.update(team_data['priest'])

    def team_center(self):
        p1 = self.warrior.pos
        p2 = self.mage.pos
        p3 = self.priest.pos
        return ((p1[0] + p2[0] + p3[0]) / 3, (p1[1] + p2[1] + p3[1]) / 3)

    def hp_sum(self):
        return sum([unit.hp for unit in self.units()])

    def units(self):
        return [self.warrior, self.mage, self.priest]

    def units_random(self):
        units = self.units()
        random.shuffle(units)
        return units

    def strongest_unit(self):
        strongest = None
        for unit in self.units_random():
            if (strongest is None or strongest.hp < unit.hp):
                strongest = unit
        return strongest

    def weakest_unit(self):
        weakest = None
        for unit in self.units_random():
            if (weakest is None or weakest.hp > unit.hp):
                weakest = unit
        return weakest

    def units_with_same_hp_as(self, unit):
        units = []
        for unit in self.units():
            if (unit.hp == unit.hp):
                units.append(unit)
        return units

    def strongest_units(self):
        return self.units_with_same_hp_as(self.strongest_unit())

    def weakest_units(self):
        return self.units_with_same_hp_as(self.weakest_unit())

    def closest_unit_from(self, target):
        closest = None
        for unit in self.units_random():
            if (closest is None or unit.distance_to(target) < closest.distance_to(target)):
                if (unit != target):
                    closest = unit
        return closest

    def farthest_unit_from(self, target):
        farthest = None
        for unit in self.units_random():
            if (farthest is None or unit.distance_to(target) > farthest.distance_to(target)):
                if (unit != target):
                    farthest = unit
        return farthest

    def units_with_distance_from(self, dist, target):
        units = []
        for unit in self.units():
            if (unit.distance_to(target) == dist):
                units.append(unit)
        return units

    def closest_units_from(self, target):
        return self.units_with_distance_from(
            self.closest_unit_from(target).distance_to(target),
            target
        )

    def farthest_units_from(self, target):
        return self.units_with_distance_from(
            self.farthest_unit_from(target).distance_to(target),
            target
        )


class Battle:
    def __init__(self, this_unit_name):
        self.this_unit_name = this_unit_name
        random.seed(int(round(time.time() * 1000)))
        self.my = Team()
        self.his = Team()
        self.her = self.his
        if (self.this_unit_name == 'warrior'):
            self.this = self.my.warrior
        elif (self.this_unit_name == 'mage'):
            self.this = self.my.mage
        elif (self.this_unit_name == 'priest'):
            self.this = self.my.priest

    def update(self, this_team_data, other_team_data, timer):
        self.my.update(this_team_data)
        self.his.update(other_team_data)
        self.timer = timer

    def distance_between(self, center, target):
        if (not isinstance(center, tuple)):
            return center.distance_to(target)
        elif (not isinstance(target, tuple)):
            return target.distance_to(center)
        else:
            return d(center, target)

    def winning_team(self):
        my_hp_sum = self.my.hp_sum()
        his_hp_sum = self.his.hp_sum()
        if (my_hp_sum > his_hp_sum):
            return (self.my, my_hp_sum - his_hp_sum)
        elif (my_hp_sum < his_hp_sum):
            return (self.his, his_hp_sum - my_hp_sum)
        else:
            return (None, 0)
