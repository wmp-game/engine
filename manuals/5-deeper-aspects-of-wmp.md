# Deeper aspects of WMP

So far we've seen the [game design](2-mechanics.md) and how those mechanics
translate into actual [gameplay](3-how-to-play.md). But what are the
implementation details behind the curtains and how can we benefit from them to
build a better AI?

## Stun

In previous versions of the WMP engine, units had their methods called even when
they were _Stunned_, which was a bit strange because they could still change/update
variables in the player's class, as if the _Stunned_ units were talking to their
teammates.

But we wanted to bring the popular feeling of helplessness that _Stun_ causes
into WMP. So, now the unit that's under the effect of _Stun_ won't be requested
to make a decision. Which means that its code won't be read until the effect of
_Stun_ wears off.

Now you know that you don't need to add lines to your code to verify if your
thinking unit is _Stunned_.

## Feeding the engine

By _feeding the engine_ we mean using `return` to express our decisions. Until
[now](4-example.md), we've been using the `battle` object to provide answers
that are recognizable by the engine. But when WMP was first designed, the `battle`
object wasn't planned at all!

#### So how were we supposed to implement our AI's?

Well, if you take a closer look at the
[`Battle`](https://github.com/arthurpaulino/wmpbattle/blob/master/wmpbattle.py)
class, its
[`update`](https://github.com/arthurpaulino/wmpbattle/blob/master/wmpbattle.py#L218)
method receives two dictionaries: `this_team_data` and `other_team_data`, besides
`timer`. And we would be aware of the battle state by navigating through those
discionaries with a set of specific keys. Horrible, isn't it? Yes! But now the
`battle` object encapsulates the battle state with intuitive attribute names for
us.

#### Okay, what about the `return` values that you wanted to talk about?

WMP players were supposed to `return` paired `(action, target)` tuples manually.
For instance, if you wanted to **Burn** the adversary's warrior with your mage,
you'd do `return ('burn', 'warrior')`. Pretty simple, right? Not so fast! Moving
was **laborious**. We had to compute specific `(x, y)` tuples to be the `target`
of `'move'` actions e-v-e-r-y-t-i-m-e. And `(x, y)` had to obey the moving
restrictions defined in the mechanics of the game, otherwise the engine would
simply ignore your command and your unit would stand still contamplating the
environment.

#### But why are you talking about old stuff if now we can simply use [`attempt_spacing`](https://github.com/arthurpaulino/wmpbattle/blob/master/wmpbattle.py#L43) or [`move_to`](https://github.com/arthurpaulino/wmpbattle/blob/master/wmpbattle.py#L88)?

Here is the thing: because we want you to do better than we did. Implement your
own methods and keep them a secret. Make _faster_ and _smarter_ methods.
`attempt_spacing` was just an incentive for you to start working on your own ideas.
Keep in mind that this is an asynchronous game and that efficiency **matters**.

`attempt_spacing` uses randomness and makes your unit wait if it fails to find a
valid `(x, y)` to move to. It **will** happen if, say, your mage is too close
from the arena boundary and you use `attempt_spacing` to go farther away from an
unit that's getting closer to you. I don't think that this kind of behaviour
would be seen on a team that makes it to the top 10.

## Be creative, you're free!

Make use of everything at your disposal. Create your own methods and class
attributes. Make smart decisions and know

* *WHEN* it's time to attack or defend

* *WHO* you should attack or defend

* And *HOW* it should be done

See you at the tournaments!
