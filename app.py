import uuid
from flask import Flask, request, jsonify
import random

app = Flask(__name__)
games = {}
ranks = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]

# Create a new game and return the game id
@app.route("/new_game", methods=["POST"])
def new_game():
    game_id = create_new_game()
    return jsonify({"game_id": game_id})

# Process a round of play for the specified game and player
@app.route("/play", methods=["POST"])
def play():
    try:
        game_id = request.json["game_id"]
        player_id = request.json["player_id"]
        result = process_round(game_id, player_id)
        if "error" in result:
            return jsonify(result), 400
        return jsonify({"message": "Round processed"})
    except KeyError:
        return jsonify({"error": "Missing game_id or player_id in the request body"}), 400
    except ValueError:
        return jsonify({"error": "Invalid game_id or player_id in the request body"}), 400

# Retrieve the current state of the specified game
@app.route("/game_state", methods=["GET"])
def game_state():
    try:
        game_id = request.args.get("game_id")
        state = get_game_state(game_id)
        if "error" in state:
            return jsonify(state), 400
        return jsonify({"state": state})
    except ValueError:
        return jsonify({"error": "Invalid game_id in the request parameter"}), 400

def create_new_game():
    game_id = generate_game_id()
    games[game_id] = create_initial_game_state()
    return game_id

def generate_game_id():
    return str(uuid.uuid4())

def create_initial_game_state():
    deck = create_deck()
    random.shuffle(deck)
    players = assign_deck(deck)
    return {
        "players": players,
        "pile": [],
        "winner": None
    }

def create_deck():
    suits = ["hearts","diamonds","clubs","spades"]
    deck = [(rank, suit) for suit in suits for rank in ranks]
    return deck

def assign_deck(deck):
    players = {}
    while len(deck)>0:
        player_id = generate_game_id()
        players[player_id] = deck[:len(deck)//2]
        deck = deck[len(deck)//2:]
    return players

def process_round(game_id, player_id):
    game = games.get(game_id)
    if not game:
        return {"error": "Invalid game id"}
    if player_id not in game["players"]:
        return {"error": "Invalid player id"}
    if not game["players"][player_id]:
        return {"error": "Player's deck is empty"}
    if game["winner"]:
        return {"error": "Game already finished"}
    player_card = game["players"][player_id].pop()
    game["pile"].append(player_card)
    for opponent_id in game["players"]:
        if game["players"][opponent_id]:
            opponent_card = game["players"][opponent_id].pop()
            game["pile"].append(opponent_card)
            break
    determine_winner(game, player_id, opponent_id, player_card, opponent_card)
    check_for_winner(game)

def determine_winner(game, player_id, opponent_id, player_card, opponent_card):
    player_rank = ranks.index(player_card[0])
    opponent_rank = ranks.index(opponent_card[0])
    if player_rank > opponent_rank:
        game["players"][player_id].extend(game["pile"])
    elif player_rank < opponent_rank:
        game["players"][opponent_id].extend(game["pile"])
    else:
        war(game, player_id, opponent_id)

def war(game, player_id, opponent_id):
    if len(game["players"][player_id])<4 or len(game["players"][opponent_id])<4:
        if len(game["players"][player_id])<4 or len(game["players"][opponent_id])<4:
        game["winner"] = None
        return
    for i in range(4):
        game["pile"].append(game["players"][player_id].pop())
        game["pile"].append(game["players"][opponent_id].pop())
    player_card = game["players"][player_id].pop()
    opponent_card = game["players"][opponent_id].pop()
    game["pile"].append(player_card)
    game["pile"].append(opponent_card)
    determine_winner(game, player_id, opponent_id, player_card, opponent_card)

def check_for_winner(game):
    for player_id in game["players"]:
        if not game["players"][player_id]:
            game["winner"] = player_id
            break

def get_game_state(game_id):
    game = games.get(game_id)
    if not game:
        return {"error": "Invalid game id"}
    return {
        "players": game["players"],
        "pile": game["pile"],
        "winner": game["winner"]
    }

if __name__ == "__main__":
    app.run()

