from engine import Engine
import random

def rnd_pos():
    return (10*random.random(), 10*random.random())

class TeamA:
    def __init__(self):
        self.name = 'Team A'

    def warrior(self, battle):
        return battle.this.move_to(rnd_pos())

    def mage(self, battle):
        return battle.this.move_to(rnd_pos())

    def priest(self, battle):
        return battle.this.move_to(rnd_pos())


class TeamB:
    def __init__(self):
        self.name = 'Team B'

    def warrior(self, battle):
        return battle.this.move_to(rnd_pos())

    def mage(self, battle):
        return battle.this.move_to(rnd_pos())

    def priest(self, battle):
        return battle.this.move_to(rnd_pos())


engine = Engine()
result = engine.start_battle(TeamA(), TeamB(), log_file='example_battle.log')
print(result)
