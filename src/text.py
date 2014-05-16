#!/usr/bin/env python
import sys, gettext

kwargs = {}
if sys.version_info[0] < 3:
    # In Python 2, ensure that the _() that gets installed into built-ins
    # always returns unicodes.  This matches the default behavior under Python
    # 3, although that keyword argument is not present in the Python 3 API.
    kwargs['unicode'] = True
gettext.install('mustyqatse', **kwargs)

header = _("Mustyqatse")

start = _("Start")

options = _("Options")
levels = _("Levels")
editor = _("Editor")

exit = _("Exit")
exitWin = _("Exit(fool!)")
exitLose = _("Exit(please)")

on_win = [
    _("Congratulations on not losing!"),
    _("You win. Not that you deserve it..."),
    _("You cheated. Admit it."),
    _("You win. The level designer must have been lazy."),
    _("Neat job. Hopefully you'll fail next time."),
    _("You fail at failing! I win at double negatives."),
    _("Good, keep playing until you lose."),
    _("I promise you will lose next round."),
]
on_lose = [
    _("Shameful, really! How could you not win?"),
    _("Try again. You might not lose as shamefully."),
    _("Do they pay you to lose or something?"),
    _("You lose too much. Seriously, I'm keeping count."),
    _("Are you exploring all the possible ways to lose?"),
    _("Wow, you've got to be creative to lose that way."),
    _("Try winning for once."),
    _("Clearly you lack the motor skills for this."),
    _("There goes the player for another loss."),
    _("The game's most loved feature says you suck."),
    _("You seem to lose often. Please stop playing."),
    _("Do you find losing amusing?"),
    _("There IS shame in losing. Feeling it yet?"),
    _("The game wins over man again."),
    _("No, you didn't win. No, I don't care."),
    _("You win at effort! But please stop bothering."),
    _("It's surprising how easily you lose."),
    _("Keep losing, who knows what happens otherwise."),
    _("Are you practicing how to lose?"),
    _("There's no end to your losing is there?"),
    _("Yet again, you lose."),
    _("You didn't do well, but that was probably your best."),
    _("There is no cheat where you win by losing."),
    _("I don't keep track of losses. Lucky you."),
    _("It almost looked like you were winning there."),
    _("No such thing as too much losing, right?"),
    _("Yes, keep playing like a Kamikaze."),
]