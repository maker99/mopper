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

from mopp import mopp, splitmessage, get_message, debug, str2bin, str2hex, bytes2bin, bytes2hex, binstring2msg, stripheader, string2stringmessage


SERVER_IP = "0.0.0.0"
UDP_PORT = 7373
CLIENT_TIMEOUT = 300
MAX_CLIENTS = 10
KEEPALIVE = 10
DEBUG = 1




receivers = {}
receivers_speed = {}


def sendto_serversock(input_data, client):
    """send a data to a mopp client 
    """
    ip, port = client.split(':')
    serversock.sendto(input_data, (ip, int(port)))


def send_text_to_client(client, speed, text_message):
    """send a text to a mopp client 
    """

    debug('%s, < "%s"(%s wpm)' % (client, text_message, speed))
    for word in text_message.split(' '):
        sendto_serversock(mopp(speed, word), client)

    return


def broadcast(input_data, excluded_client):
    """broadcast a text to everyone except one mopp client 
    """
    for c in receivers.keys():
        if c == excluded_client:
            continue

        debug("%s, Broadcasting " % c)
        sendto_serversock(input_data, c)


def welcome(client, speed):
    client_number = str(len(receivers))
    receivers[client] = time.time()
    debug("%s, New client %s" % (client, client_number))

    send_text_to_client(client, speed, 'hi ' + client_number + ' pse k')


def reject(client, speed):
    debug('%s, Rejecting' % client)
    send_text_to_client(client, speed, ':qrl K')


def enroll_new_client(client, speed):
    if (len(receivers) < MAX_CLIENTS):
        receivers[client] = time.time()
        receivers_speed[client] = speed
        welcome(client, receivers_speed[client])
    else:
        reject(client, speed)
        debug("ERR: maximum clients reached")


if __name__ == "__main__":
    # connect to local hosts port 7373
    try:
        serversock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        serversock.bind((SERVER_IP, UDP_PORT))
    except:
        print ("error: Port %s is already in use, maybe an earlier chatServer?" % (UDP_PORT))
        print ("try: ps xwww | grep -i chatserver" )
        exit(-1)
        
    serversock.settimeout(KEEPALIVE)
    debug("Server started, listening on %s:%s" % (SERVER_IP, UDP_PORT))

    while KeyboardInterrupt:
        time.sleep(0.2)						# anti flood
        try:
            input_bytes, addr = serversock.recvfrom(64)

            client = addr[0] + ':' + str(addr[1])

            (speed, message_text, b_protocol, b_serial_number) = \
            get_message(input_bytes)

            if client in receivers:
                if (message_text == ':bye') or (message_text == '<sk>'):
                    #   if stripheader(input_data) == stripheader(mopp(20, ':bye')):
                    debug("%s, removing client on request" % client)
                    send_text_to_client(client, speed, 'bye K e e')
                    del receivers[client]
                    del receivers_speed[client]
                else:
                    # broadcast this message to everyone else
                    broadcast(input_bytes, client)
                    receivers[client] = time.time()
            else:
                if (message_text == 'k') or (message_text == 'hi'):
                    enroll_new_client(client, speed)
                else:
                    send_text_to_client(client, speed, '?')
                    debug("%s, is unknown client, ignoring" % client)

        except socket.timeout:
            # Send UDP keepalives
            for c in receivers.keys():
                ip, port = c.split(':')
                debug("%s, Timeout and renewing" % c)
                serversock.sendto(b'', (ip, int(port)))
                # serversock.sendto(mopp(speed,'ee' ), (ip, int(port)))
            pass

        # except (KeyboardInterrupt, SystemExit):
        except ():
            serversock.close()
            break

        # clean clients list
        clients_to_be_removed = []
        for c in receivers.items():
            if c[1] + CLIENT_TIMEOUT < time.time():
                clients_to_be_removed.append(c[0])

        for client in clients_to_be_removed:
            debug("%s, removing expired client" % client)
            send_text_to_client(client, receivers_speed[client], 'bye K e e')
            del receivers[client]
            del receivers_speed[client]
