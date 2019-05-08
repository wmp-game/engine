# How to play

WMP is played by implementing a class that defines a team. The constructor sets
the name of the team.

```python
def __init__(self):
  self.name = 'Team Name'
```

And the methods `warrior`, `mage` and `priest` implement the behavior of the team
members (units). Each of these methods run on its own thread as an asynchronous
loop.

```python
def warrior(self, battle):
  # reason here
  return ...

def mage(self, battle):
  # think here
  return ...

def priest(self, battle):
  # decide here
  return ...
```

Notice the `battle` object, for it's the big deal here! It contains:

1. Information about the timer and all units in play
2. Methods to derive information about the battle state
3. Methods to get proper objects to feed the engine with `return ...`

The `battle` object is an instance of the `Battle` class, which is defined and
documented at the [wmpbattle](https://github.com/arthurpaulino/wmpbattle)
repository. Check it out :)

**Important:** if a player implements a method that takes longer than 0.1s to
`return`, he enters the **danger zone** and his account is subject to due
penalties.
