# engine

This is the heart of WMP.

## Running WMP

Instantiate `WMP`:

```python
wmp = WMP()
```

Then call the `start_battle` method passing the teams instances and the
`log_file` (default is `'battle.log'`) as arguments:

```python
team_a = SomeTeamClassA()
team_b = SomeTeamClassB()
wmp.start_battle(team_a, team_b, log_file='awesome_battle.log')
```

### The `start_battle`'s output

The `start_battle` method returns a tuple `(success, value)`.

If `success == True`, the battle log will be stored in a file located at the
`battle_logs` folder and `value` means the following:

* `1`: `team_a` wins;
* `-1`: `team_b` wins;
* `0`: the battle tied.

If `success == False`, the log will be ignored and `value` means the following:

* `1`: `team_a` took too long to think;
* `-1`: `team_b` took too long to think;
* `0`: the game was interrupted for some unkown reason.

### Example

`example.py` contains classes with dummy teams. Run `$ python example.py` to see
what happens.

## Log lines patterns

* Finishing the battle

    `winner|<team_name>`

    or

    `draw`

* Error during reasoning process

    `<timer>|<team_name>|<unit>|error`

* `wait` action

    `<timer>|<team_name>|<unit>|wait|<duration>`

* `move` action

    `<timer>|<team_name>|<unit>|move|<x_orig>,<y_orig>|<x_dest>,<y_dest>`

* Other actions

    `<timer>|<team_name>|<unit>|<action>|<target>|<effectiveness>`

* Acquiring status

    `<timer>|<team_name>|<unit>|+sts|<status>|<duration>`

* Losing status

    `<timer>|<team_name>|<unit>|-sts|<status>`

* Cooldown activation

    `<timer>|<team_name>|<unit>|+cd|<skill>|<duration>`

* Cooldown deactivation

    `<timer>|<team_name>|<unit>|-cd|<skill>`

* Damage over time

    `<timer>|<team_name>|<unit>|-hp|<damage>`

# WMP components

The [`target`](#target) keyword will be used to represent an object that can be
either a `(x, y)` tuple or an instance of [`Unit`](#unit).

## Battle

[`Battle`](#battle) represents the current state of a battle.

Let `battle` be an instance of [`Battle`](#battle).

### Attributes

* `battle.my` points to the player's [`team`](#team)

* `battle.his` and `battle.her` point to the adversary's [`team`](#team)

* `battle.timer` is a `float` that tells how many seconds are left before the
battle ends

* `battle.this` is a shortcut to get the thinking [`unit`](#unit)

    For instance, if you're inside the `priest` method, `battle.this` points
    to the same object as `battle.my.priest` (see [`Team`](#team))

### Methods

* `battle.distance_between(target1, target2)` returns the
[euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) between
[`target1`](#target) and [`target2`](#target)

* `battle.winning_team()` returns a tuple `(winning_team, hp_difference)`

    * If the battle is tied, `winning_team` is `None` and `hp_difference` is
    equal to 0

    * If there's a team is ahead, `winning_team` points to the winning
    [`team`](#team) and `hp_difference` is a positive `float` that tells the
    difference of health points between the teams

## Team

[`Team`](#team) represents the current state of a team.

Let `team` be an instance of [`Team`](#team).

### Attributes

* `team.warrior` points to the [`warrior`](#unit) of `team`

* `team.mage` points to the [`mage`](#unit) of `team`

* `team.priest` points to the [`priest`](#unit) of `team`

### Methods

* `team.team_center()` returns a `(x, y)` tuple that represents the mean position
of the `team` members

* `team.hp_sum()` returns the sum of the `team` members' health points

* `team.units()` returns the list `[team.warrior, team.mage, team.priest]`

* `team.units_random()` returns a randomly shuffled `team.units()`

* `team.strongest_unit()` returns a random [`unit`](#unit) amongst those who
have the highest hp in `team`

* `team.weakest_unit()` returns a random [`unit`](#unit) amongst those who
have the lowest hp in `team`

* `team.units_with_same_hp_as(unit)` returns a list containing the
[`units`](#unit) that have the same amount of health points as `unit`

* `team.strongest_units()` is a shortcut for
`team.units_with_same_hp_as( team.strongest_unit() )`

* `team.weakest_units()` is a shortcut for
`team.units_with_same_hp_as( team.weakest_unit() )`

* `team.closest_unit_from(target)` returns a random [`unit`](#unit) from `team`
amongst those who are the closest ones from [`target`](#target)

* `team.farthest_unit_from(target)` returns a random [`unit`](#unit) from `team`
amongst those who are the farthest ones from [`target`](#target)

* `team.units_with_distance_from(dist, target)` returns a list of
[`units`](#unit) from `team` that are at a distance `dist` from [`target`](#target)

* `team.closest_units_from(target)` is a shortcut for

  ```python
  team.units_with_distance_from(
      # the distance to the closest unit:
      team.closest_unit_from(target).distance_to(target),
      # the referential:
      target
  )
  ```

* `team.farthest_units_from(target)` is a shortcut for

  ```python
  team.units_with_distance_from(
      # the distance to the farthest unit:
      team.farthest_unit_from(target).distance_to(target),
      # the referential:
      target
  )
  ```

## Unit

[`Unit`](#unit) represents the current state of an unit.

Let `unit` be an instance of [`Unit`](#unit).

### Attributes

* `unit.pos` is a `(x, y)` tuple that informs the position of the unit

* `unit.hp` is a `float` that informs the unit's health points

* `unit.sts` points to the ['Sts'](#sts) object of `unit`

* `unit.cds` points to the ['Cds'](#cds) object of `unit`

### Methods

* `unit.distance_to(target)` returns the distance between `unit` and
[`target`](#target)

The following methods are used to answer back to the engine.

* `unit.wait(duration)` makes the the unit wait for `duration` seconds

* `unit.attempt_spacing(target, ideal_distance)` is pretty neat!
It makes the `unit` try to place itself at a distance of `ideal_distance` from
[`target`](#target).

    If `attempt_spacing` fails to find a proper position, it will return
    `unit.wait(0.01)`

* `unit.move_to(target)` is a shortcut for `unit.attempt_spacing(target, 0.0)`

The following methods are used for character-specific skills. If you use them
with the wrong character, the engine will ignore it and your unit will just stand
still for 1s.

Also, using a skill on a target from the wrong team will make your unit try to
use the skill on the proper team. For instance, if you tell your priest to heal
the adversary's warrior, he will try to heal your own warrior.

So, call:

* `unit.hit(unit)` to use **Hit** on [`unit`](#unit)

* `unit.bash(unit)` to use **Bash** on [`unit`](#unit)

* `unit.burn(unit)` to use **Burn** on [`unit`](#unit)

* `unit.freeze(unit)` to use **Freeze** on [`unit`](#unit)

* `unit.heal(unit)` to use **Heal** on [`unit`](#unit)

* `unit.silence(unit)` to use **Silence** on [`unit`](#unit)

## Sts

[`Sts`](#sts) represents the current statuses of an [`unit`](#unit).

Let `sts` be an instance of `Sts`.

### Attributes

* `sts.stun` tells how long until _Stun_ wears off

* `sts.burning` tells how long until _Burning_ wears off

* `sts.freezing` tells how long until _Freezing_ wears off

* `sts.silenced` tells how long until _Silenced_ wears off

## Cds

[`Cds`](#cds) represents the current cooldowns of an [`unit`](#unit).

Let `cds` be an instance of `Cds`.

### Attributes

The attributes of `cds` depend on the `unit` that instantiated it.

Warriors can access `cds.bash` to know how long until **Bash** becomes available.

Priests can access `cds.silence` to know how long until **Silence** becomes
available.
