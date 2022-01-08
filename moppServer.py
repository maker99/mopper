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

    def __init__(self, ip, port, timer, speed, status ):
        self.ip = ip
        self.port = port
        self.timer = timer
        self.speed = None
        self.status = None
        
    def id(self):
        return  self.create_id(self.ip,self.port)
    
    def create_id(ip,port):
        return  ip + ':' + port
    
    

class MoppServer:

    
    MAX_CLIENTS = 10
    CLIENT_TIMEOUT = 60
    DEBUG = 1

    def __init__(self):
        self.receivers = {}
        self.receivers_speed = {}
        self.clients = {}

    def debug(self,str):
      if self.DEBUG:
          # print str
          print("%s: %s" % (time.strftime("%Y-%m-%d %H%M%S"), str))



    def sendto_client(self,server, client_id, data):
        """send a data to a mopp client 
        """
        ip, port = client_id.split(':')
        server.sendto(ip, int(port), data)


    def broadcast(self,server, data, excluded_client):
        """broadcast a text to everyone except one mopp client 
        """
        for c in self.receivers.keys():
            if c == excluded_client:
                continue

            self.debug("%s, Broadcasting " % c)
            self.sendto_client(server, c, data)


    def send_text_to_client(self,server, client_id, m, speed, text_message):
        """send a text to a mopp client 
        """

        self.debug('%s, < "%s"(%s wpm)' % (client_id, text_message, speed))
        for word in text_message.split(' '):
            self.sendto_client(server, client_id, m.mopp(speed, word))


    def welcome(self,server, client_id, m, speed):
        number_of_clients = str(len(self.receivers))
        self.receivers[client_id] = time.time()
        self.debug("%s, New client %s" % (client_id, number_of_clients))

        self.send_text_to_client(server, client_id, m, speed,
                            'hi ' + number_of_clients + ' pse k')


    def reject(self,server, client_id, m, speed):
        self.debug('%s, Rejecting' % client_id)
        self.send_text_to_client(server, client_id, m, speed, ':qrl K')


    def enroll_new_client(self,server, client_id, m, speed):
        if (len(self.receivers) < self.MAX_CLIENTS):
            # client = MoppClient(ip, port,time.time(), speed)
            # clients.append()
            self.receivers[client_id] = time.time()
            self.receivers_speed[client_id] = speed
            self.welcome(server, client_id, m, self.receivers_speed[client_id])
        else:
            self.reject(client_id, speed)
            self.debug("ERR: maximum clients reached")


    def process_message(self, S, input_bytes, addr):
        
        client_id = addr[0] + ':' + str(addr[1])
        client_ip = addr[0]
        client_port = str(addr[1])

        (speed, message_text, b_protocol, b_serial_number) = \
            m.get_message(input_bytes)

        if client_id in self.receivers:
            if (message_text == ':bye') or (message_text == '<sk>') or (message_text == 'K'):
                #   if stripheader(input_data) == stripheader(mopp(20, ':bye')):
                self.debug("%s, removing client on request" % client_id)
                self.send_text_to_client(S, client_id, m, speed, 'K e e')
                del self.receivers[client_id]
                del self.receivers_speed[client_id]
            else:
                # broadcast this message to everyone else
                self.broadcast(S, input_bytes, client_id)
                self.receivers[client_id] = time.time()
        else:
            if (message_text == 'k') or (message_text == 'hi'):
                self.enroll_new_client(S, client_id, m, speed)
            else:
                self.send_text_to_client(S, client_id, m, speed, '? hi')
                self.debug("%s, is unknown client, ignoring" % client_id)


    def cleanup(self, m, S, MS):
        # clean clients list
        clients_to_be_removed = []
        for c in self.receivers.items():
            if c[1] + self.CLIENT_TIMEOUT < time.time():
                clients_to_be_removed.append(c[0])

        for client in clients_to_be_removed:
            self.debug("%s, removing expired client" % client)
            self.send_text_to_client(
                    S, client, m, self.receivers_speed[client], 'K e e')
            del self.receivers[client]
            del self.receivers_speed[client]

if __name__ == "__main__":

    m = Mopp()
    S = Server()
    MS = MoppServer()
    

    S.start()

    while KeyboardInterrupt:
        time.sleep(0.2)						# anti flood

        input_bytes, addr = S.getInput()
        
        if addr is not None:
            MS.process_message(S, input_bytes, addr)
        else:
            # Send UDP keepalives
            MS.broadcast(S, b'', None)

        MS.cleanup(m, S, MS)
    
    S.stop()