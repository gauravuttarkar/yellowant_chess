"""Code which actually takes care of application API calls or other business logic"""
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass ,MessageButtonsClass
from yellowant_api.models import UserIntegration
import chess
import chess.uci
from yellowant_message_builder.messages import items_message, item_message

MOVE_FLAG = 0
#0 for White, 1 for Black

move_dict = {
    0 : "White",
    1 : "Black"
}

def color_inv(c):
    if c=="w":
        return "Black"

    else:
        return "White"

def color(c):
    if c=="b":
        return "Black"

    else:
        return "White"


def moveFlag(a):
    global MOVE_FLAG
    if a==0:
        MOVE_FLAG=1
    else:
        MOVE_FLAG = 1

def chooseColor(args,user_integration):
    m = MessageClass()
    data = {'list': []}
    data['list'].append({"Color": "White"})
    data['list'].append({"Color": "Black"})
    m.data = data
    return m



def playComputer(args,user_integration):
    object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    board = chess.Board(object.board_state)
    engine = chess.uci.popen_engine("/Users/Gaurav/Desktop/Yellowant/chess/Stockfish/src/stockfish")
    col = color(object.board_state[-12])
    engine.position(board)
    move = engine.go(movetime=2000)
    board.push(chess.Move.from_uci(str(move[0])))
    m = MessageClass()
    if board.is_insufficient_material():
        print("Insufficient material")
        m.message_text = "Insufficient material"
        return m

    if board.is_stalemate():
        print("Stalemate")
        m.message_text = "Stalemate"

    if board.is_checkmate():
        print("Computer wins")
        m.message_text = "Checkmate !! \n"+col + " wins"
        return m

    object.board_state = board.fen()
    object.save()

    attachment = MessageAttachmentsClass()
    attachment.image_url="http://www.fen-to-image.com/image/36/double/coords/"+board.fen()[:-13]

    button = MessageButtonsClass()
    button.text = "Make move"
    button.value = "Make move"
    button.name = "Make move"
    button.command = {"service_application": str(user_integration.yellowant_integration_id), "function_name": "makemove",\
                      "inputs": ["move"],
                      "data" : {"move":"testing"}
                      }
    attachment.attach_button(button)

    button1 = MessageButtonsClass()
    button1.text = "Play Computer"
    button1.value = "Play Computer"
    button1.name = "Play Computer"
    button1.command = {"service_application": str(user_integration.yellowant_integration_id), "function_name": "playcomputer", \
                       "data": {"move": "testing"}
                      }
    attachment.attach_button(button1)

    m.attach(attachment)

    return m



def startGame(args,user_integration):


    object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    board = chess.Board()
    object.board_state = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    object.save()
    print("inside start game")
    print(user_integration.id)
    m = MessageClass()
    color = args['Color']
    if color == "White":
        MOVE_FLAG = 0
    else:
        MOVE_FLAG = 1

    #board = chess.Board()

    m.message_text = "You chose " + color
    attachment = MessageAttachmentsClass()

    print(color + " to move")

    if (color=="Black"):
        m = playComputer(args,user_integration)
        return m

    attachment.image_url = "http://www.fen-to-image.com/image/36/double/coords/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    field1 = AttachmentFieldsClass()
    field1.title = "Move"
    field1.value = move_dict[MOVE_FLAG] + " to move"
    attachment.attach_field(field1)
    button = MessageButtonsClass()
    button.text = "Make move"
    button.value = "Make move"
    button.name = "Make move"
    button.command = {
        "service_application": str(user_integration.yellowant_integration_id),
        "function_name": "makemove",
        "inputs": ["move"],
        "data": {"move": "testing"},
    }
    attachment.attach_button(button)

    button1 = MessageButtonsClass()
    button1.text = "Play Computer"
    button1.value = "Play Computer"
    button1.name = "Play Computer"
    button1.command = {"service_application": str(user_integration.yellowant_integration_id), "function_name": "playcomputer",
                       "data": {"move": "testing"},
                      }
    attachment.attach_button(button1)

    m.attach(attachment)


    #m.image_url = "http://www.fen-to-image.com/image/rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    return m

#
def showBoard(args,user_integration):

    print(user_integration.yellowant_integration_id)
    object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    board = chess.Board(object.board_state)
    print(object.board_state)

    m = MessageClass()
    m.message_text = color(object.board_state[-12])  + " to move"
    attachment = MessageAttachmentsClass()
    attachment.image_url="http://www.fen-to-image.com/image/36/double/coords/"+board.fen()[:-13]
    button = MessageButtonsClass()
    button.text = "Make move"
    button.value = "Make move"
    button.name = "Make move"
    button.command = {"service_application": str(user_integration.yellowant_integration_id), "function_name": "makemove",\
                      "inputs": ["move"],
                      "data" : {"move":"testing"}
                      }
    attachment.attach_button(button)
    m.attach(attachment)

    return m


def makeAMove(args,user_integration):

    print('hello')
    object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    board = chess.Board(object.board_state)
    print(args)
    move = args.get('move')

    m = MessageClass()
    print(object.board_state)
    print(object.board_state[-12])
    col = color_inv(object.board_state[-12])
    print(col)
    m.message_text = col + " to move"
    move_uci = board.parse_san(move)
    if move_uci in board.legal_moves:
        board.push_san(move)
        if board.is_insufficient_material():
            print("Insufficient material")
            m.message_text = "Insufficient material"

        if board.is_stalemate():
            print("Stalemate")
            m.message_text = "Stalemate"
        if board.is_checkmate():
            print(col + " wins")
            m.message_text = col + " wins"

        object.board_state = board.fen()
        object.save()
    else:
        m.message_text = "Invalid move"
        return m



    attachment = MessageAttachmentsClass()
    button = MessageButtonsClass()
    button.text = "Make move"
    button.value = "Make move"
    button.name = "Make move"
    button.command = {"service_application": str(user_integration.yellowant_integration_id), "function_name": "makemove",\
                      "inputs": ["move"],
                      "data" : {"move":"testing"}
                      }
    attachment.attach_button(button)

    button1 = MessageButtonsClass()
    button1.text = "Play Computer"
    button1.value = "Play Computer"
    button1.name = "Play Computer"
    button1.command = {"service_application": str(user_integration.yellowant_integration_id),
                      "function_name": "playcomputer",
                      "data": {"move": "testing"}
                      }
    attachment.attach_button(button1)

    attachment.image_url="http://www.fen-to-image.com/image/36/double/coords/"+board.fen()[:-13]

    m.attach(attachment)

    return m


