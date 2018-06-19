"""Mapping for command invoke name to logic"""
from .commands import startGame,chooseColor, showBoard, makeAMove , playComputer


COMMANDS_BY_INVOKE_NAME = {
"startgame" : startGame,
"choosecolor" : chooseColor,
"showboard" : showBoard,
"makemove" : makeAMove,
"playcomputer" : playComputer
}
