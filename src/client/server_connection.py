import sys, os
__file_dir__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(__file_dir__, '..')))

from common.connection import Connection
from common.consts import *

class ServerConnection(Connection):
    def __init__(self, server_socket):
        self._socket = server_socket

    def __repr__(self):
        return "<Server>"

    def move(self, direction):
        self.send_data({'type': MOVE, 'direction': direction})

    def add_tile(self, x, y):
        self.send_data({'type': ADD_ITEM, 'x': x, 'y': y})

    def get_update(self, player, world):
        for event in self.get_events():
            player.rect.x = event['player']['x']
            player.rect.y = event['player']['y']
            for x, y in event['updates']:
                self.world.add_tile(x,y)
