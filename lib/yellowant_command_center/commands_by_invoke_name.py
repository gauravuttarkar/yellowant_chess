"""Mapping for command invoke name to logic"""
from .commands import startGame,chooseColor, showBoard, makeAMove , playComputer, playAgainst, accept, startGameAgainstPlayer,\
                      makeMoveAgainst


COMMANDS_BY_INVOKE_NAME = {
"startgame" : startGame,
"choosecolor" : chooseColor,
"showboard" : showBoard,
"makemove" : makeAMove,
"playcomputer" : playComputer,
"playagainst" : playAgainst,
"accept" : accept,
"startgameplayer" : startGameAgainstPlayer,
"makemoveagainst" : makeMoveAgainst

}
