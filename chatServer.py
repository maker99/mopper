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

MAX_CLIENTS = 10
CLIENT_TIMEOUT = 300

DEBUG = 1

receivers = {}
receivers_speed = {}


def debug(str):
    if DEBUG:
        # print str
        print("%s: %s" % (time.strftime("%Y-%m-%d %H%M%S"), str))


def sendto_client(server, client, data):
    """send a data to a mopp client 
    """
    ip, port = client.split(':')
    server.sendto(ip, int(port), data)


def broadcast(server, data, excluded_client):
    """broadcast a text to everyone except one mopp client 
    """
    for c in receivers.keys():
        if c == excluded_client:
            continue

        debug("%s, Broadcasting " % c)
        sendto_client(server, c, data)


def send_text_to_client(server, client, m, speed, text_message):
    """send a text to a mopp client 
    """

    debug('%s, < "%s"(%s wpm)' % (client, text_message, speed))
    for word in text_message.split(' '):
        sendto_client(server, client, m.mopp(speed, word))


def welcome(server, client, m, speed):
    client_number = str(len(receivers))
    receivers[client] = time.time()
    debug("%s, New client %s" % (client, client_number))

    send_text_to_client(server, client, m, speed,
                        'hi ' + client_number + ' pse k')


def reject(server, client, m, speed):
    debug('%s, Rejecting' % client)
    send_text_to_client(server, client, m, speed, ':qrl K')


def enroll_new_client(server, client, m, speed):
    if (len(receivers) < MAX_CLIENTS):
        receivers[client] = time.time()
        receivers_speed[client] = speed
        welcome(server, client, m, receivers_speed[client])
    else:
        reject(client, speed)
        debug("ERR: maximum clients reached")


def process_message(S, input_bytes, addr):
    client = addr[0] + ':' + str(addr[1])

    (speed, message_text, b_protocol, b_serial_number) = \
        m.get_message(input_bytes)

    if client in receivers:
        if (message_text == ':bye') or (message_text == '<sk>') or (message_text == 'K'):
            #   if stripheader(input_data) == stripheader(mopp(20, ':bye')):
            debug("%s, removing client on request" % client)
            send_text_to_client(S, client, m, speed, 'bye K e e')
            del receivers[client]
            del receivers_speed[client]
        else:
            # broadcast this message to everyone else
            broadcast(S, input_bytes, client)
            receivers[client] = time.time()
    else:
        if (message_text == 'k') or (message_text == 'hi'):
            enroll_new_client(S, client, m, speed)
        else:
            send_text_to_client(S, client, m, speed,
                                '? hi')
            debug("%s, is unknown client, ignoring" % client)


if __name__ == "__main__":

    m = Mopp()
    S = Server()

    S.start()

    while KeyboardInterrupt:
        time.sleep(0.2)						# anti flood

        input_bytes, addr = S.getInput()
        if addr is not None:
            process_message(S, input_bytes, addr)
        else:
            # Send UDP keepalives
            broadcast(S, b'', None)

        # clean clients list
        clients_to_be_removed = []
        for c in receivers.items():
            if c[1] + CLIENT_TIMEOUT < time.time():
                clients_to_be_removed.append(c[0])

        for client in clients_to_be_removed:
            debug("%s, removing expired client" % client)
            send_text_to_client(
                S, client, m, receivers_speed[client], 'bye K e e')
            del receivers[client]
            del receivers_speed[client]
    
    S.stop()