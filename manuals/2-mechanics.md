# Mechanics

## Asynchronicity: there are no turns!

This is a striking feature of WMP. If you have ever played real time PvP games
like [World of Warcraft](https://worldofwarcraft.com) or
[Battlerite](https://www.battlerite.com/) you know how it feels.

So, how does the WMP engine prevents the players from spamming thousands of skills
per second?

We've implemented a lower bound of 0.01 seconds between actions. More specifically,
the time interval between actions are defined by the following rules:

1. After [waiting](#waiting), units will be requested to perform a new action
instantly

2. After [moving](#moving), units will be requested to perform a new action after
`X` seconds where `X` is the distance traveled

3. After performing [interactive actions](#interactive-actions), units will be
requested to perform a new action 1s later

## Waiting

Units are allowed to wait. The waiting duration time can vary from 0.01s to 1s.

## Moving

The longest [euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance)
that an unit is allowed to move is 1m and the shortest is 0.01m.

The arena is not a grid. You are free to occupy any position in the square area
defined by the points `(0, 0)`, `(30, 0)`, `(0, 30)` and `(30, 30)`.

One team starts with its units at the points `(13, 10)`, `(15, 10)` and`(17, 10)`.
The units of the other team start at the points `(13, 20)`, `(15, 20)` and
`(17, 20)`.

## Interactive Actions

### Melee actions

Melee actions can't reach shorter than 0.2m nor longer than 1m and their
effectiveness are calculated by the formula `-32.0*(d-0.2)*(d-1.0)`, where `d` is
the distance to the target.

### Magic actions

Magic actions are either short or long-ranged

#### Short-ranged magic actions

Can't reach longer than 3m and their effectiveness are calculated by the
formula `-(d-3.0)*(d+3.0)/2`, where `d` is the distance to the target.

#### Long-ranged magic actions

Can't reach shorter than 3m nor longer than 5m and their effectiveness are
calculated by the formula `-3.0*(d-3.0)*(d-5.0)`, where `d` is the distance to
the target.

## Units

### The warrior

The warrior can use **Hit** and **Bash**.

* **Hit** is a [melee action](#melee-actions). It causes `MLE` damage, where `MLE`
is calculated by the melee effectiveness formula

* **Bash** is a [melee action](#melee-actions). It causes _Stun_ for `MLE` seconds
and has a cooldown of `2*MLE` seconds, where `MLE` is calculated by the melee
effectiveness formula

### The mage

The mage can use **Burn** and **Freeze**.

* **Burn** is a [long-ranged magic action](#long-ranged-magic-actions). It causes
`LRM` damage, removes _Freezing_ and causes _Burning_ for `2*LRM` seconds, where
`LRM` is calculated by the long-ranged magic effectiveness formula

* **Freeze** is a [short-ranged magic action](#short-ranged-magic-actions). It
causes `SRM/2` damage, removes _Burning_ and causes _Freezing_ for `2*SRM`
seconds, where `SRM` is calculated by the short-ranged magic effectiveness formula

### The priest

The priest can use **Heal** and **Silence**.

* **Heal** is a [defensive magic action](#defensive-magic-actions). It removes
_Burning_ and _Freezing_ and regenerates `DM` health points, where `DM` is
calculated by the defensive magic effectiveness formula

* **Silence** is an [offensive magic action](#offensive-magic-actions). It causes
_Silenced_ for `OM` seconds and has a cooldown of `2*OM` seconds, where `OM` is
calculated by the offensive magic effectiveness formula

## Status

* _Stun_ paralizes the unit completely

* _Burning_ causes `0.2` damage per second

* _Freezing_ makes an unit move only half of the distance and **providing
  distances greater than 1m won't work regardless**

* _Silenced_ prevents units from using special abilities such as
  **Bash**, **Burn**, **Freeze**, **Heal** and **Silence**
