# Gameplay example

Now let's create an example to explore the versatility of the `battle` object.

Our code will reflect the following strategy:

* We will try to exploit the mage's close combat limitations, so our focus
priority will be:

    1. Mage
    2. Priest
    3. Warrior

* Warrior:

    * If we have **Bash** available, we can stun our target and improve our spacing
    for higher damage

    * If our warrior's hp is low (say lower than 20), we run to our priest like
    a small kitten

* Mage:

    * Our mage will help our warrior to kill the target with **Burn**

    * We will try to keep the adversary's warrior away with **Freeze** as we run
    away from him

* Priest:

    * Our priest will try to place himself at the center of the team to increase
    his chance of having enough range for **Heal**

    * We will try to keep the adversary's priest _Silenced_, so he won't heal his
    warrior and our mage will have a better time running away

    * If the adversary's priest is dead, we silence the mage. So our silencing
    priority is the following:

        1. Priest
        2. Mage
        3. Warrior

    * If our team has someone under 20 hp, we tell our priest to come closer to
    him and heal

Let's begin!

```python
class BestTeamEver:
    def __init__(self):
        self.name = 'Best Team Ever!'

    # let's implement a method that tells us who we should focus on according to
    # our strategy
    def focused_adversary(self, battle):
        if (battle.his.mage.hp > 0): return battle.his.mage
        elif (battle.his.priest.hp > 0): return battle.his.priest
        else: return battle.his.warrior

    # and a method to know who we should be silencing
    def silence_focus(self, battle):
        if (battle.his.priest.hp > 0): return battle.his.priest
        elif (battle.his.mage.hp > 0): return battle.his.mage
        else: return battle.his.warrior

    def warrior(self, battle):
        # first, we check our hp
        if (battle.this.hp >= 20):
            # ok, we're fine!
            # let's see who we should focus on
            focused_adversary = self.focused_adversary(battle)

            # how far are we?
            distance = battle.this.distance_to(focused_adversary)

            # let's aim for a distance of 0.6m!
            if (distance < 0.3 or 0.9 < distance):
                return battle.this.attempt_spacing(focused_adversary, 0.6)
            else:
                # we're close enough!
                # let's check if the unit is stunned
                if (focused_adversary.sts.stun > 0):
                    # find the perfect spacing
                    if (battle.this.distance_to(focused_adversary) != 0.6):
                        return battle.this.attempt_spacing(focused_adversary, 0.6)
                    else:
                        # THIS! IS! SPARTA! AAAAAAAAAH!!!!!
                        return battle.this.hit(focused_adversary)
                else:
                    # so, he's not stunned...
                    # let's see if Bash is available
                    if (battle.this.cds.bash == 0):
                        # smash him!
                        return battle.this.bash(focused_adversary)
                    else:
                        # hit him! might not do too much damage, though
                        return battle.this.hit(focused_adversary)
        else:
            # low hp! run to the hills!
            return battle.this.move_to(battle.my.priest)

    def mage(self, battle):
        # let's take a look at the adversary's warrior. he's scary.
        distance = battle.this.distance_to(battle.his.warrior)
        # and let's keep in mind who our focused adversary is
        focused_adversary = self.focused_adversary(battle)
        if (distance > 1.5 or battle.his.warrior.hp == 0):
            # is 1.5m fine? you tell me! but if the warrior is dead we should be
            # fine, shouldn't we? :)

            # let's find a way to Burn the focused adversary
            dist = battle.this.distance_to(focused_adversary)
            if (3.3 < dist and dist < 4.7):
                # the ideal dist is 4m. but i think this will do
                return battle.this.burn(focused_adversary)
            else:
                # we can try to place ourselves at the perfect distance
                return battle.this.attempt_spacing(focused_adversary, 4)
        else:
            # warrior is too close! if he's already freezing we can run
            if (battle.his.warrior.sts.freezing > 0):
                # let's find a good place to run to

                # we can imagine a grid inside the arena and search for the best
                # spot
                best_spot = None
                for x in range(5, 30, 5):
                    for y in range(5, 30, 5):
                        spot = (x, y)
                        # we're looking for a place that's farther than 3m away
                        # from the warrior. I think 3m is safe enough
                        dist = battle.distance_between(spot, battle.his.warrior)
                        if (dist > 3):
                            # we also want the best spot for us to Burn the focused
                            # adversary
                            if (best_spot is None):
                                best_spot = spot
                            else:
                                best_dist = battle.distance_between(best_spot, focused_adversary)
                                spot_dist = battle.distance_between(spot, focused_adversary)
                                # the best spot is the one whose distance to the
                                # focused adversary is as close to 4m as possible
                                if (abs(spot_dist-4) < abs(best_dist-4)):
                                    best_spot = spot
                # now we know where to run to
                return battle.this.move_to(best_spot)
            else:
                # the adversary's warrior is not Freezing. Freeze him!
                return battle.this.freeze(battle.his.warrior)

    def priest(self, battle):
        # as a priority, let's see if someone is too weak
        weakest = battle.my.weakest_unit()
        # notice that it's ok if our weakest unit is the priest himself
        if (weakest.hp < 20):
            # let's try to get closer. I think 1.5m should be fine
            if (battle.this.distance_to(weakest) > 1.5):
                # we should try to be as close as possible
                return battle.this.move_to(weakest)
            else:
                # now we heal
                return battle.this.heal(weakest)
        else:
            # now suppose that the team is fine (according to our definition of
            # "fine" haha)

            # let's focus on positioning over agressiveness
            dist_to_center = battle.this.distance_to(battle.my.team_center())
            # 1.5m should be fine, I guess
            if (dist < 1.5):
                # let's try to Silence someone
                silence_focus = self.silence_focus(battle)
                # we're not going for perfect Silences
                dist_to_focus = battle.this.distance_to(silence_focus)
                if (3.3 < dist_to_focus and dist_to_focus < 4.7):
                    # good enough. Silence! I kill you!
                    return battle.this.silence(silence_focus)
                else:
                    # let's improve our spacing
                    return battle.this.attempt_spacing(silence_focus, 4)
            else:
                # let's try to reach the perfect positioning to the team center
                return battle.this.move_to(battle.my.team_center())
```

Oh my! Even coding this example was quite fun. I wonder how this piece of beauty
would perform against other minds.

Anyway, could you spot some flaws in the strategy? Let me begin with a few

* What if our warrior is expecting help from a dead body?

* That way of looking for a good spot with the mage smells a bit fishy and seems
to be a little too slow, don't you think?

* I just assumed that the adversary's warrior was chasing our mage when, in fact,
he could be doing something completely different!

* The priest is simply ignoring eventualities like _Freezing_ and _Burning_ on
his team

* The priest will wait until someone is under 20hp to help him. How lazy!

* I didn't look at the `timer` to see how far behind or ahead we are in order to
adapt our strategy accordingly

Okay, okay, I know, this was just an example. I bet you can do better!
