#!/usr/bin/python
import sys, json, xmpp, random, string
 
# Authentication data for Google Cloud Messaging
SERVER = 'gcm.googleapis.com'
PORT = 5235
USERNAME = "389849193267"
PASSWORD = "AIzaSyD3-Rl6eRc-_EiRIl404F3OySyS4T6ILZo"
 
unacked_messages_quota = 1000
send_queue = []

# list of Game objects
current_games = []

# Game class for storing game information
class Game:

  def __init__(self,code):
    self.gameCode = code
    # list of Player objects
    self.players = []

  def addPlayer(self,player):
    self.players.append(player)

# Player class for storing player's name, registration id, and technology list
class Player:

  def __init__(self,name,regId):
    self.name = name
    self.techs = []
    self.regId = regId

  def set_reg_id(self,regId):
    self.regId = regId

  def add_tech(self,tech):
    self.techs.append(tech)


# Return a random alphanumeric id
def random_id():
  rid = ''
  for x in range(8): rid += random.SystemRandom().choice(string.ascii_letters + string.digits)
  return rid

# Generate a random alphanumeric 5 digit string for game identification
def gen_game_code():
  return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))

def message_callback(session, message):
  global unacked_messages_quota
  gcm = message.getTags('gcm')
  if gcm:
    gcm_json = gcm[0].getData()
    msg = json.loads(gcm_json)
    if not msg.has_key('message_type'):
      # Acknowledge the incoming message immediately.
      send({"to": msg["from"],
            "message_type": "ack",
            "message_id": msg["message_id"]})
      msg_data = msg['data']

      # Check if they want to start a new game
      if msg_data.has_key('new_game'):
        # Create new game
        game = Game(gen_game_code())
        # Create new player object
        player = Player(msg_data['new_game'], msg_data['reg_id'])
        # Add player to game
        game.addPlayer(player)
        # Add game to game list
        current_games.append(game)
        # DEBUG
        print "New Game!"
        print "Game Code: " + current_games[-1].gameCode
        print "Player Name: " + player.name
        print "Player Reg Id: " + player.regId
        # Tell player their game was successfully created
        send_queue.append({"to": msg["from"],
                           "message_id": random_id(),
                           "data": {"message": {"game_code": game.gameCode}}})

      # Check if someone wants to join a game
      elif msg_data.has_key('join_game'):
        game_code = msg_data['join_game']
        print 'Join Game: ' + game_code
        for game in current_games:
          if game.gameCode == game_code:
            # Create new player object
            player = Player(msg_data['player_name'], msg_data['reg_id'])
            # Add player to selected game
            game.addPlayer(player)
            # DEBUG
            print "Join Game!"
            print "Game Code: " + game.gameCode
            for person in game.players:
              print "Player Name: " + person.name
              print "Player Reg Id: " + person.regId

            send_queue.append({"to": msg["from"],
                           "message_id": random_id(),
                           "data": {"message": {"game_code": game_code}}})
            break;

      # Handle a player having a new technology
      elif msg_data.has_key('new_tech'):
        # Update player tech list
        for game in current_games:
          if game.gameCode == msg_data['game_code']:
            for player in game.players:
              if player.name == msg_data['player_name']:
                player.techs.append(msg_data['new_tech'])
              else:
                send_queue.append({"to": player.regId,
                           "message_id": random_id(),
                           "data": {"message": {"new_tech": msg_data['new_tech'],
                                                "player_name": msg_data['player_name']}}})
            break;
      # Ping app to ensure connection exists.
      elif msg.has_key('from'):
        # Send a dummy echo response back to the app that sent the upstream message.
        send_queue.append({"to": msg["from"],
                           "message_id": random_id(),
                           "data": {"message": {"ping": 1}}})
    elif msg['message_type'] == 'ack' or msg['message_type'] == 'nack':
      unacked_messages_quota += 1
 
def send(json_dict):
  template = ("<message><gcm xmlns=\"google:mobile:data\">{1}</gcm></message>")
  client.send(xmpp.protocol.Message(
      node=template.format(client.Bind.bound[0], json.dumps(json_dict))))
 
def flush_queued_messages():
  global unacked_messages_quota
  while len(send_queue) and unacked_messages_quota > 0:
    send(send_queue.pop(0))
    unacked_messages_quota -= 1
 
# Begin 'main'
client = xmpp.Client('gcm.googleapis.com', debug=['socket'])
client.connect(server=(SERVER,PORT), secure=1, use_srv=False)
auth = client.auth(USERNAME, PASSWORD)
if not auth:
  print 'Authentication failed!'
  sys.exit(1)
 
client.RegisterHandler('message', message_callback)
 
while True:
  client.Process(1)
  flush_queued_messages()