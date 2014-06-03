###
# Copyright (c) 2014, Bryan Kok
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# I'm not sure how to properly attribute code and will be seeking advice as
# to how to do so; I have greatly drawn on
# this library: https://github.com/bfontaine/term2048 as a starting point
# to implement 2048 in text mode.
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import math
from board import Board

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Supy2048')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class Game(object):

    def __init__(self, colors={},
	 mode=None, azmode=False, **kws):
	"""
Create a new game.
scores_file: file to use for the best score (default
is ~/.term2048.scores)
colors: dictionnary with colors to use for each tile
mode: color mode. This adjust a few colors and can be 'dark' or
'light'. See the adjustColors functions for more info.
other options are passed to the underlying Board object.
"""
	self.board = Board(**kws)
	self.score = 0

	self.__colors = colors
	self.__azmode = azmode


    def boardToString(self, margins={}):
	"""
	return a string representation of the current board.
	"""
	b = self.board
	rg = range(b.size())
	left = ' '*margins.get('left', 0)
	s = '\n'.join(
	    [left + ' '.join([self.getCellStr(x, y) for x in rg]) for y in rg])
	return s

    def __str__(self, margins={}):
	b = self.boardToString(margins=margins)
	top = '\n'*margins.get('top', 0)
	bottom = '\n'*margins.get('bottom', 0)
	scores = ' \tScore: %5d\n' % (self.score)
	return top + b.replace('\n', scores, 1) + bottom


    def incScore(self, pts):
	"""
update the current score by adding it the specified number of points
"""
	self.score += pts

    def getCellStr(self, x, y):  # TODO: refactor regarding issue #11
	"""
	return a string representation of the cell located at x,y.
	"""
	c = self.board.getCell(x, y)
	az = {}
	tempclass = Supy2048(callbacks.Plugin)
	colors = tempclass.getColors()
	for i in range(1, int(math.log(self.board.goal(), 2))):
	    az[2 ** i] = chr(i + 96)

	if c == 0 and self.__azmode:
	    return '.'
	elif c == 0:
	    return '  .'

	elif self.__azmode:
	    if c not in az:
		return '?'
	    s = az[c]
	elif c == 1024:
	    s = ' 1k'
	elif c == 2048:
	    s = ' 2k'
	else:
	    s = '%3d' % c
#	print str(colors[int(math.log(c, 2) % len(colors))])
	return "\x03"+ str(colors[int(math.log(c, 2) % len(colors))])+s+"\x03"
	# colors[] is a list of mIRC color codes.

class Supy2048(callbacks.Plugin):
    """Add the help for "@plugin help Supy2048" here
    This should describe *how* to use this plugin."""
    threaded = True
    def __init__(self, irc):
	self.privategames = {}
	self.__parent = super(Supy2048, self)
	self.__parent.__init__(irc)

#    def showboardstatus(self, msg):
#	return self.privategames[msg.prefix+"-"+irc.network].__str__(margins={'left': 0, 'top': 0, 'bottom': 0}).split("\n"):
    def getColors(self):
	return self.registryValue('colors')

    def checkgamefinished(self, gameID):
        if not (self.privategames[gameID].board.won() or self.privategames[gameID].board.canMove()):
		self.privategames.pop(gameID, None)
		if not self.privategames[gameID].board.canMove():
			return "You Won!"
		if not self.privategames[gameID].board.canMove():
			return "Game Over!"

        else: return ""

    def startsingleplayer(self, irc, msg, args):
        """Starts a single player game of 2048 in query."""
	if msg.prefix+"-"+irc.network in self.privategames:
		irc.reply("You have already started a game")
		return
	self.privategames[msg.prefix+"-"+irc.network] = Game({})
   	for s in self.privategames[msg.prefix+"-"+irc.network].__str__(margins={'left': 0, 'top': 0, 'bottom': 0}).split("\n"):
		irc.reply(s)
		#print s

    startsingleplayer = wrap(startsingleplayer, ['private'])
 
    def up(self, irc, msg, args):
	"""2048 board up"""
	if msg.prefix+"-"+irc.network not in self.privategames:
		irc.reply("Please start the game first.")
	
	else:
		self.privategames[msg.prefix+"-"+irc.network].incScore(self.privategames[msg.prefix+"-"+irc.network].board.move(Board.UP))
		for s in self.privategames[msg.prefix+"-"+irc.network].__str__(margins={'left': 0, 'top': 0, 'bottom': 0}).split("\n"):
	                irc.reply(s)
		gameFinished = self.checkgamefinished(msg.prefix+"-"+irc.network)
		if not gameFinished:
			pass
		else: 
			irc.reply((gameFinished))
			

    def down(self, irc, msg, args):

	"""2048 board down"""
	if msg.prefix+"-"+irc.network not in self.privategames:
                irc.reply("Please start the game first.")

        else:
                self.privategames[msg.prefix+"-"+irc.network].incScore(self.privategames[msg.prefix+"-"+irc.network].board.move(Board.DOWN))
		for s in self.privategames[msg.prefix+"-"+irc.network].__str__(margins={'left': 0, 'top': 0, 'bottom': 0}).split("\n"):
	                irc.reply(s)
		gameFinished = self.checkgamefinished(msg.prefix+"-"+irc.network)
                if not gameFinished:
                        pass
                else:
                        irc.reply((gameFinished))

    def left(self, irc, msg, args):
	"""2048 board left"""
	if msg.prefix+"-"+irc.network not in self.privategames:
                irc.reply("Please start the game first.")

        else:
                self.privategames[msg.prefix+"-"+irc.network].incScore(self.privategames[msg.prefix+"-"+irc.network].board.move(Board.LEFT))
		for s in self.privategames[msg.prefix+"-"+irc.network].__str__(margins={'left': 0, 'top': 0, 'bottom': 0}).split("\n"):
	                irc.reply(s)
		gameFinished = self.checkgamefinished(msg.prefix+"-"+irc.network)
                if not gameFinished:
                        pass
                else:
                        irc.reply((gameFinished))

    def right(self, irc, msg, args):
	"""2048 board right"""
	if msg.prefix+"-"+irc.network not in self.privategames:
                irc.reply("Please start the game first.")

        else:
                self.privategames[msg.prefix+"-"+irc.network].incScore(self.privategames[msg.prefix+"-"+irc.network].board.move(Board.RIGHT))
		for s in self.privategames[msg.prefix+"-"+irc.network].__str__(margins={'left': 0, 'top': 0, 'bottom': 0}).split("\n"):
	                irc.reply(s)
		gameFinished = self.checkgamefinished(msg.prefix+"-"+irc.network)
                if not gameFinished:
                        pass
                else:
                        irc.reply((gameFinished))

    def stopgame(self, irc, msg, args):
	"""Stop 2048"""
	if msg.prefix+"-"+irc.network not in self.privategames:
                irc.reply("No game started")
	else:
		self.privategames.pop(msg.prefix+"-"+irc.network, None)
		irc.reply("Game stopped.")

Class = Supy2048


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
