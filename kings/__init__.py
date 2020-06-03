from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random

BLK_CARDS = "🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃞🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂮"
RED_CARDS = "🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂾🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃎"
BACK_CARD = "🂠"

app = Flask(__name__)
app.config["SECRET_KEY"] = "lolsosecret"
socketio = SocketIO(app)


class Deck:
    def __init__(self):
        self.cards = self.shuffle()

    def shuffle(self):
        return random.sample(BLK_CARDS + RED_CARDS, len(BLK_CARDS + RED_CARDS)) + [BACK_CARD]

    def format_card(self, card):
        if card in BACK_CARD:
            return f'<font style="color:blue">{card}</font>'
        if card in RED_CARDS:
            return f'<font style="color:red">{card}</font>'
        else:
            return card

    def draw(self):
        if self.cards:
            self.cards.pop()
            return self.top_card()
        else:
            return "╳", 0

    def top_card(self):
        return self.format_card(self.cards[-1]), len(self.cards)

    def reset(self):
        self.cards = self.shuffle()
        return self.top_card()


global deck
deck = Deck()


@app.route("/", methods=["GET"])
def index():
    card, size = deck.top_card()
    return render_template("index.html", card=card, size=size)


@socketio.on("joinGame")
def join_game(event):
    print("A new player joined: " + str(event))
    emit("playerJoined", event, broadcast=True)


@socketio.on("drawCard")
def draw_card(event):
    card, size = deck.draw()
    event.update({"card": card, "size": size})
    print("A card was drawn: " + str(event))
    emit("cardDrawn", event, broadcast=True)


@socketio.on("resetGame")
def reset_game(event):
    card, size = deck.reset()
    event.update({"card": card, "size": size})
    print("Game was reset: " + str(event))
    emit("cardDrawn", event, broadcast=True)
