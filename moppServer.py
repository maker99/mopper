#!/usr/local/bin/python
# -*- coding: latin-1 -*-
#
# an implementation of the mopp protocol for Morserino-32
# based on https://github.com/sp9wpn/m32_chat_server
# the protocol description is:  https://github.com/oe1wkl/Morserino-32/blob/master/Documentation/Protocol%20Description/morse_code_over_packet_protocol.md
#
#
import socket
import time

from mopp import Mopp
from server import Server


class MoppClient:

    def __init__(self, ip, port, timer, speed, status):
        self.ip = ip
        self.port = port
        self.timer = timer
        self.speed = None
        self.status = None

    def id(self):
        return self.create_id(self.ip, self.port)

    def create_id(ip, port):
        return ip + ':' + port


class MoppServer:

    MAX_CLIENTS = 10
    CLIENT_TIMEOUT = 60
    DEBUG = 1

    def __init__(self, mopp, server):
        self.receivers = {}
        self.receivers_speed = {}
        self.clients = {}
        self.mopp = mopp
        self.server = server

    def debug(self, str):
        if self.DEBUG:
            # print str
            print("%s: %s" % (time.strftime("%Y-%m-%d %H%M%S"), str))

    def send_raw(self, client_id, raw_data):
        """send a data to a mopp client, data includes speed info
        """
        ip, port = client_id.split(':')
        self.server.sendto(ip, int(port), raw_data)

    def send_text(self, client_id, text_message, speed=None):
        """send a text to a mopp client, either with client's speed or supplied speed
        """
        if speed == None:
            speed = self.receivers_speed[client_id]
        self.debug('%s, < "%s"(%s wpm)' % (client_id, text_message, speed))
        for word in text_message.split(' '):
            self.send_raw(client_id, self.mopp.mopp(speed, word))

    def broadcast_text(self, text, excluded_client=None):
        """broadcast a text to everyone except one mopp client 
           Note: this text will be send in each client's own speed
        """
        self.debug("Broadcasting %s" % text)
        for client_id in self.receivers.keys():
            if client_id == excluded_client:
                continue

            self.sendtext(client_id, text)
        self.debug("Broadcasting %s" % text)

    def broadcast_raw(self, data=b'', excluded_client=None):
        """broadcast a raw message to everyone except to excluded_client 
           Note: speed is defined by data
        """
        for client_id in self.receivers.keys():
            if client_id == excluded_client:
                continue

            self.debug("%s, Broadcasting " % client_id)
            self.send_raw(client_id, data)


    def add_client(self, client_id, speed):
        client_number = str(len(self.receivers) + 1)
        if (int(client_number) < self.MAX_CLIENTS):
            self.debug("%s, New client %s" % (client_id, client_number))
            self.receivers[client_id] = time.time()
            self.receivers_speed[client_id] = speed
            self.send_text(client_id, 'hi ' + client_number + ' pse k')
        else:
            self.debug("ERR: maximum clients reached")
            self.send_text(client_id, ':qrl K', speed)
            self.remove_client(client_id)

    def remove_client(self, client_id):
        self.debug("%s, removing expired client" % client_id)
        self.send_text(client_id, 'K e e')
        del self.receivers[client_id]
        del self.receivers_speed[client_id]

    def renew_client(self, client_id, speed=None):
        self.receivers[client_id] = time.time()
        if speed != None:
            self.receivers_speed[client_id] = speed

    def cleanup_clients(self):
        # clean clients list
        clients_to_be_removed = []
        for c in self.receivers.items():
            if c[1] + self.CLIENT_TIMEOUT < time.time():
                clients_to_be_removed.append(c[0])
        
        for client in clients_to_be_removed:        
            self.remove_client(client)

    def process_message(self, input_bytes, addr):

        client_ip = addr[0]
        client_port = str(addr[1])
        client_id = client_ip + ':' + client_port

        (speed, message_text, b_protocol, b_serial_number) = \
            self.mopp.get_message(input_bytes)

        if client_id in self.receivers:
            if (message_text == ':bye') or (message_text == '<sk>') or (message_text == 'K'):
                self.remove_client(client_id)
            else:
                # broadcast this message to everyone else
                self.broadcast_raw(input_bytes, client_id)
                self.renew_client(client_id, speed)
        else:
            if (message_text == 'k') or (message_text == 'hi'):
                self.add_client(client_id, speed)
            else:
                self.debug("%s, is unknown client, ignoring" % client_id)
                # answer unknown client with own speed
                self.send_text(client_id, '? hi', speed)


if __name__ == "__main__":

    moppInstance = Mopp()
    serverInstance = Server()
    serverInstance.start()  # TODO: error handling

    MS = MoppServer(moppInstance, serverInstance)

    while KeyboardInterrupt:
        time.sleep(0.2)						# anti flood

        input_bytes, addr = serverInstance.getInput()

        if addr is not None:
            MS.process_message(input_bytes, addr)
        else:
            # Send UDP keepalives to all connected clients
            MS.broadcast_raw()

        # cleanup expired clients
        MS.cleanup_clients()

    # stop the server
    serverInstance.stop()
