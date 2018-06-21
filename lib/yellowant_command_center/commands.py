"""Code which actually takes care of application API calls or other business logic"""
from yellowant.messageformat import MessageClass, MessageAttachmentsClass, AttachmentFieldsClass ,MessageButtonsClass
from ..yellowant_api.models import UserIntegration
import chess
import chess.uci
import uuid
from yellowant import YellowAnt



INITIAL_BOARD = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

INITIAL_BOARD_REST = " w KQkq - 0 1"
IMAGE_URL = "http://www.fen-to-image.com/image/36/double/coords/"

MOVE_FLAG = 0
#0 for White, 1 for Black

"""
Functions to return colors.
"""
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



def chooseColor(args,user_integration):
    """
    Picklist function to return colors.
    """
    m = MessageClass()
    data = {'list': []}
    data['list'].append({"Color": "White"})
    data['list'].append({"Color": "Black"})
    m.data = data
    return m



def playAgainst(args,user_integration):
    """
    Function which sends the invite to other players to play chess.
    """
    opponent_id = args.get("yellowant_user_id")
    opponent_object = UserIntegration.objects.get(yellowant_integration_id=opponent_id)
    player_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)

    webhook_message = MessageClass()
    webhook_message.message_text = "Chess Invite"
    attachment = MessageAttachmentsClass()
    field1 = AttachmentFieldsClass()
    field1.title = "You have been invited to play chess with "
    field1.value = player_object.yellowant_team_subdomain

    button = MessageButtonsClass()
    button.text = "Accept Invitation"
    button.value = "Accept Invitation"
    button.name = "Accept Invitation"
    button.command = {
                      "service_application": str(opponent_object.yellowant_integration_id),
                      "function_name": "accept",
                      "data": {"user_int": player_object.yellowant_integration_id }
                     }
    attachment.attach_button(button)
    attachment.attach_field(field1)
    webhook_message.attach(attachment)
    access_token = opponent_object.yellowant_integration_token
    yellowant_user_integration_object = YellowAnt(access_token=access_token)

    print("Printing webhook")
    send_message = yellowant_user_integration_object.create_webhook_message(
        requester_application=opponent_object.yellowant_integration_id,
        webhook_name="webhook", **webhook_message.get_dict())


    m = MessageClass()
    m.message_text = "Waiting for response from opponent"

    return m



def accept(args,user_integration):
    """
    Function to accept the invitation from another player.
    """
    opponent_user_integration = args.get("user_int")

    state = str(uuid.uuid4())

    opponent_object = UserIntegration.objects.get(yellowant_integration_id=opponent_user_integration)
    opponent_object.playing_state = state
    player_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    player_object.playing_state = state

    player_object.opponent_integration_id = opponent_object.yellowant_integration_id
    opponent_object.opponent_integration_id = player_object.yellowant_integration_id

    player_object.board_state = INITIAL_BOARD + INITIAL_BOARD_REST
    opponent_object.board_state = INITIAL_BOARD + INITIAL_BOARD_REST

    player_object.save()
    opponent_object.save()


    webhook_message = MessageClass()
    webhook_message.message_text = "Chess Invite"
    attachment = MessageAttachmentsClass()
    field1 = AttachmentFieldsClass()
    field1.title = "Your Chess Invite has been accepted by"
    field1.value = player_object.yellowant_team_subdomain

    button = MessageButtonsClass()
    button.text = "Start Game"
    button.value = "Start Game"
    button.name = "Start Game"
    button.command = {
                      "service_application" : str(opponent_object.yellowant_integration_id),
                      "function_name" : "startgameplayer",
                      "data" : {"user_int": player_object.yellowant_integration_id},
                      "inputs" :  ["Color"]
                     }
    attachment.attach_button(button)
    attachment.attach_field(field1)
    webhook_message.attach(attachment)

    access_token = opponent_object.yellowant_integration_token
    yellowant_user_integration_object = YellowAnt(access_token=access_token)

    send_message = yellowant_user_integration_object.create_webhook_message(
        requester_application=opponent_object.yellowant_integration_id,
        webhook_name="webhook", **webhook_message.get_dict())

    m = MessageClass()
    return m











def playComputer(args,user_integration):
    """
    Function to play against the Computer.
    """
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
    print(IMAGE_URL + board.fen()[:-13])
    attachment.image_url = IMAGE_URL + board.fen()[:-13]

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

    button2 = MessageButtonsClass()
    button2.text = "Accept Invitation"
    button2.value = "Accept Invitation"
    button2.name = "Accept Invitation"
    button2.command = {
                      "service_application" : str(user_integration.yellowant_integration_id),
                      "function_name" : "accept",
                      "data" : {"user_int": user_integration.yellowant_integration_id }
                     }
    attachment.attach_button(button2)


    m.attach(attachment)

    return m






def startGameAgainstPlayer(args,user_integration):
    """

    """


    player_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)

    opponent_object = UserIntegration.objects.get(yellowant_integration_id=player_object.opponent_integration_id)

    board = chess.Board(player_object.board_state)
    color = args['Color']

    attachment = MessageAttachmentsClass()

    print(color + " to move")

    if (color=="Black"):
        webhook_message = MessageClass()
        webhook_message.message_text = "You are playing White!"
        attachment = MessageAttachmentsClass()
        button = MessageButtonsClass()
        button.text = "Make Move"
        button.value = "Make Move"
        button.name = "Make Move"
        button.command = {
            "service_application": str(opponent_object.yellowant_integration_id),
            "function_name": "makemoveagainst",
            "data": {"user_int": player_object.yellowant_integration_id},
        }
        attachment.attach_button(button)

        webhook_message.attach(attachment)
        access_token = opponent_object.yellowant_integration_token
        yellowant_user_integration_object = YellowAnt(access_token=access_token)

        send_message = yellowant_user_integration_object.create_webhook_message(
            requester_application=opponent_object.yellowant_integration_id,
            webhook_name="webhook", **webhook_message.get_dict())

        return

    else:
        print("Inside else")
        m = MessageClass()
        attachment = MessageAttachmentsClass()
        attachment.image_url = IMAGE_URL + INITIAL_BOARD
        m.message_text = "Make a Move"
        field1 = AttachmentFieldsClass()
        field1.title = "Move"
        field1.value = color + " to move"
        attachment.attach_field(field1)

        attachment.image_url = IMAGE_URL + INITIAL_BOARD


        button = MessageButtonsClass()
        button.text = "Make Move"
        button.value = "Make Move"
        button.name = "Make Move"
        button.command = {
            "service_application": str(player_object.yellowant_integration_id),
            "function_name": "makemoveagainst",
            "inputs": ["move"],
            "data": {"user_int": player_object.yellowant_integration_id},
        }
        attachment.attach_button(button)

        m.attach(attachment)

        return m






def makeMoveAgainst(args,user_integration):
    player_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    opponent_object = UserIntegration.objects.get(yellowant_integration_id=player_object.opponent_integration_id)

    access_token = opponent_object.yellowant_integration_token
    yellowant_user_integration_object = YellowAnt(access_token=access_token)

    move = args.get("move")
    board = chess.Board(player_object.board_state)
    col = color_inv(player_object.board_state[-12])

    m = MessageClass()

    m.message_text = col + " to move"
    move_uci = board.parse_san(move)
    if move_uci in board.legal_moves:
        board.push_san(move)
        if board.is_insufficient_material():
            print("Insufficient material")
            m.message_text = "Insufficient material"
            endGame(args, user_integration)

            webhook_message = MessageClass()
            webhook_field = AttachmentFieldsClass()
            webhook_field.title = "Result"
            webhook_field.value = "Game drawn due to insufficient material"
            attachmentImage = MessageAttachmentsClass()
            attachmentImage.image_url = IMAGE_URL + board.fen()[:-13]
            attachmentImage.attach_field(webhook_field)
            webhook_message.attach(attachmentImage)





        if board.is_stalemate():
            print("Stalemate")
            m.message_text = "Stalemate"
            endGame(args, user_integration)
        if board.is_checkmate():
            print(col + " wins")
            m.message_text = col + " wins"
            endGame(args, user_integration)

        player_object.board_state = board.fen()
        opponent_object.board_state = board.fen()

        player_object.save()
        opponent_object.save()



    else:
        m.message_text = "Invalid move"
        return m

    attachment = MessageAttachmentsClass()
    attachment.image_url = IMAGE_URL + board.fen()[:-13]

    m.attach(attachment)
    webhook_message = MessageClass()
    webhook_field = AttachmentFieldsClass()
    webhook_field.title = "Move"
    webhook_field.value = col + " to move"
    attachmentImage = MessageAttachmentsClass()
    attachmentImage.attach_field(webhook_field)
    attachmentImage.image_url = IMAGE_URL + board.fen()[:-13]

    button = MessageButtonsClass()
    button.text = "Make Move"
    button.value = "Make Move"
    button.name = "Make Move"
    button.command = {
        "service_application": str(opponent_object.yellowant_integration_id),
        "function_name": "makemoveagainst",
        "inputs": ["move"],
        "data": {"user_int": player_object.yellowant_integration_id},
    }
    attachmentImage.attach_button(button)

    webhook_message.attach(attachmentImage)



    send_message = yellowant_user_integration_object.create_webhook_message(
        requester_application=opponent_object.yellowant_integration_id,
        webhook_name="webhook", **webhook_message.get_dict())

    return m













def startGame(args,user_integration):


    object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    board = chess.Board()
    object.board_state = INITIAL_BOARD + INITIAL_BOARD_REST
    object.save()
    print("inside start game")
    print(user_integration.id)
    m = MessageClass()
    color = args['Color']
    # if color == "White":
    #     MOVE_FLAG = 0
    # else:
    #     MOVE_FLAG = 1
    #
    # #board = chess.Board()

    m.message_text = "You chose " + color
    attachment = MessageAttachmentsClass()

    print(color + " to move")

    if (color=="Black"):
        m = playComputer(args,user_integration)
        return m

    print(IMAGE_URL + INITIAL_BOARD)
    attachment.image_url = IMAGE_URL + INITIAL_BOARD
    field1 = AttachmentFieldsClass()
    field1.title = "Move"
    field1.value = color + " to move"
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
    attachment.image_url = IMAGE_URL + board.fen()[:-13]
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
    print(user_integration.yellowant_integration_id)
    object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    print(object.id)
    print(object.board_state)
    board = chess.Board(object.board_state)
    print(board)
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

    attachment.image_url = IMAGE_URL + board.fen()[:-13]

    m.attach(attachment)

    return m


def endGame(args,user_integration):
    """
    Function to end the game between two players.
    """

    player_object = UserIntegration.objects.get(yellowant_integration_id=user_integration.yellowant_integration_id)
    opponent_object = UserIntegration.objects.get(yellowant_integration_id=player_object.opponent_integration_id)
    opponent_object.opponent_integration_id = None
    player_object.opponent_integration_id = None
    return





