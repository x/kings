from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import itertools

BLK_CARDS = "🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃜🃝🃞🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂬🂭🂮"
RED_CARDS = "🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂼🂽🂾🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃌🃍🃎"
BACK_CARD = "🂠"

app = Flask(__name__, static_url_path='/static')
app.config["SECRET_KEY"] = "lolsosecret"
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


class Deck:
    def __init__(self):
        self.cards = self.shuffle()

    def shuffle(self):
        return random.sample(BLK_CARDS + RED_CARDS, len(BLK_CARDS + RED_CARDS)) + [
            BACK_CARD
        ]

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


class Players:
    def __init__(self):
        self.players = []
        self.current_player_gen = None
        self.next_player_gen = None
        self.current_player = None
        self.next_player = None
        self.current_player_idx = None

    def reset(self):
        self.shuffle()
        self.set_active_players()

    def set_active_players(self):
        if len(self.players) == 0:
            self.current_player = None
            self.next_player = None
            return

        current_player_idx = 0
        if self.current_player:
            for i, _ in enumerate(self.players):
                if self.players[i]['id'] == self.current_player['id']:
                    current_player_idx = i
                    break
            else:  # We didn't find a match. The current active player left
                current_player_idx = self.current_player_idx

        self.current_player_idx = current_player_idx

        # Generator cycles the list of players indefinitely
        # islice cycles through until we get back to the current player
        self.current_player_gen = itertools.islice(
            itertools.cycle(self.players), current_player_idx, None
        )
        self.next_player_gen = itertools.islice(
            itertools.cycle(self.players), current_player_idx, None
        )
        self.next_player = next(self.next_player_gen)

    def next_players(self):
        self.current_player = next(
            self.current_player_gen) if self.current_player_gen else None
        self.next_player = next(
            self.next_player_gen) if self.next_player_gen else None

    def shuffle(self):
        self.players = random.sample(self.players, len(self.players))

    def add_player(self, player):
        self.players.append(player)
        self.set_active_players()

    def remove_player(self, player):
        self.players = [
            p for p in self.players if p['id'] != player['id']
        ]
        self.set_active_players()

    def update_player(self, player):
        for i, _ in enumerate(self.players):
            if self.players[i]['id'] == player['id']:
                self.players[i]['name'] = player['name']
                return True
        return False


global deck
global players
deck = Deck()
players = Players()


@ app.route("/", methods=["GET"])
def index():
    card, size = deck.top_card()
    return render_template("index.html", card=card, size=size)


@ socketio.on("joinGame")
def join_game(event):
    print("A new player joined: " + str(event))
    players.add_player(event['user'])
    if not players.current_player:
        players.next_players()

    event['currentPlayer'] = players.current_player
    event['nextPlayer'] = players.next_player
    emit("playerJoined", event, broadcast=True)


@ socketio.on('leaveGame')
def leave_game(event):
    print("Player has left: " + str(event))
    players.remove_player(event['user'])
    event['currentPlayer'] = players.current_player
    event['nextPlayer'] = players.next_player
    emit("playerLeft", event, broadcast=True)


@ socketio.on("drawCard")
def draw_card(event):
    card, size = deck.draw()
    players.next_players()
    event.update({
        "card": card,
        "size": size,
        "currentPlayer": players.current_player,
        "nextPlayer": players.next_player,
    })
    print("A card was drawn: " + str(event))
    emit("cardDrawn", event, broadcast=True)


@ socketio.on("resetGame")
def reset_game(event):
    card, size = deck.reset()
    players.reset()
    event.update({
        "card": card,
        "size": size,
        "currentPlayer": players.current_player,
        "nextPlayer": players.next_player,
    })
    print("Game was reset: " + str(event))
    emit("cardDrawn", event, broadcast=True)


@ socketio.on("updatePlayerName")
def update_player_name(event):
    players.update_player(event['user'])
    print("Players name updated: " + str(event))
    emit("playersNameUpdated", event, broadcast=True)


@ socketio.on("disconnect")
def disconnect():
    # FIX: No idea who disconnected abruptly. Figure that out and handle it.
    print("A player disconnected")
