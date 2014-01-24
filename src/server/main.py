# Author : MM
# Purpose: Run the game server

import sys, os
__file_dir__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(__file_dir__, '..')))

import pygame as pg
from pygame.locals import *
from pygame.sprite import Sprite, Group, spritecollide

from common.player import Player
from common.consts import *
from common.world import *

import socket
import threading
import time
import select

from client_connection import *

pg.init()

# Listen on all connections
SERVER_IP   = '0.0.0.0'
SERVER_PORT = 1337
SERVER_ADDR = (SERVER_IP, SERVER_PORT)
MAX_CLIENTS = 1

class ServerGame(object):
    def __init__(self):
        self.player = Player()
        self.world = World(WIDTH/T_P, HEIGHT/T_P)
        self.clients = []
        self.updates = []

    def run(self):
        self.connect_players()
        while True:
            CLOCK.tick(FPS)
            self.get_actions()
            self.player.update(self.world)
            self.update_clients()

    def connect_players(self):
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(SERVER_ADDR)
        sock.listen(MAX_CLIENTS)
        while len(self.clients) < MAX_CLIENTS:
            host, endpoint = sock.accept()
            # TODO: Change 0 to role
            new_client = GameClient(host, endpoint, 0)
            print "Accepted new client:", repr(new_client)
            self.clients.append(new_client)

    def get_actions(self):
        clients_with_actions = select.select(self.clients, [], [], 0)
        for client in clients_with_actions[0]:
            for event in client.get_events():
                try:
                    if event['type'] == MOVE:
                        self.handle_move(client, event)
                    elif event['type'] == ADD_ITEM:
                        self.handle_add_item(client, event)
                except:
                    print "Error handling", event, "from", client

    def handle_move(self, client, event):
        if event['direction'] == LEFT:
            self.player.walking_left = True
        elif event['direction'] == RIGHT:
            self.player.walking_right = True
        elif event['direction'] == JUMP:
            if self.player.on_ground(self.world):
                self.player.jump()

    def handle_add_item(self, client, event):
        x = event['x']
        y = event['y']
        self.world.add_tile(x, y)
        self.updates.add((x,y))

    def update_clients(self):
        for client in self.clients:
            client.send_data({'player': {'x': self.player.rect.x, 'y': self.player.rect.y},
                'updates': self.updates})
        self.updates = []

if __name__ == '__main__':
    ServerGame().run()
