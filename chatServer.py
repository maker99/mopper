#!/usr/local/bin/python
# -*- coding: latin-1 -*-
#
# https://github.com/sp9wpn/m32_chat_server
#
import socket
import time

from mopp import mopp, splitmessage, debug, str2bin, str2hex, bytes2bin, bytes2hex, binstring2msg, stripheader, string2stringmessage
SERVER_IP = "0.0.0.0"
UDP_PORT = 7373
CLIENT_TIMEOUT = 300
MAX_CLIENTS = 10
KEEPALIVE = 10
DEBUG = 1

serversock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serversock.bind((SERVER_IP, UDP_PORT))
serversock.settimeout(KEEPALIVE)
debug("Server started, listening on %s:%s" % (SERVER_IP,UDP_PORT))

receivers = {}
receivers_speed = {}

def sendto_serversock(input_data,client):
    ip, port = client.split(':')
    serversock.sendto(input_data, (ip, int(port)))


def send_text_to_client(client, speed, text_message):
  """send a number of mopp words from a text 
  """

  debug('%s, < "%s"' % (client,text_message))
  for word in text_message.split(' '):
    sendto_serversock(mopp(speed,word), client) 

  return 


def broadcast(input_data, client):
    for c in receivers.keys():
        if c == client:
            continue

        debug("%s, Broadcasting " % c)
        sendto_serversock(input_data, c)


def welcome(client, speed):
    client_number = str(len(receivers))
    receivers[client] = time.time()
    debug("%s, New client %s" % (client,client_number))

    send_text_to_client(client, speed, 'hi ' + client_number + ' pse k' )


def reject(client, speed):
    debug('%s, Rejecting' % client)
    send_text_to_client(client, speed, ':qrl K')


while KeyboardInterrupt:
    time.sleep(0.2)						# anti flood
    try:
        input_bytes, addr = serversock.recvfrom(64)

        client = addr[0] + ':' + str(addr[1])

        (b_protocol, b_serial_number, b_speed, b_data) = splitmessage(input_bytes)
        speed = int(b_speed,2)
        message_text = binstring2msg(b_data)

        debug('==============')
        debug('%s > "%s" -> %s' % (client, bytes2bin(input_bytes), input_bytes.hex(':')))
        debug('--- Header ---' )
        debug('%s             = protocol version: %s' % ( b_protocol,int(b_protocol,2)))
        debug('  %s       = serial number   : %s'     % ( b_serial_number,int(b_serial_number,2)))
        debug('        %s = speed           : %s wpm' % ( b_speed,int(b_speed,2)))
        debug('--- Data ---' )
        debug('%s = "%s"' % (b_data, message_text))
        debug('==============')
        

        if client in receivers:
            if  (message_text == ':bye') or (message_text == '<sk>'):
                #   if stripheader(input_data) == stripheader(mopp(20, ':bye')):
                debug("%s, removing client on request" % client)
                send_text_to_client(client, speed, 'bye K e e')
                del receivers[client]
                del receivers_speed[client]
            else:
                broadcast(input_bytes, client)
                receivers[client] = time.time()
        else:
            if  (message_text == 'k') or (message_text == 'hi'):
                #   if stripheader(input_data) == stripheader(mopp(20, 'hi')):
                if (len(receivers) < MAX_CLIENTS):
                    receivers[client] = time.time()
                    receivers_speed[client] = speed
                    welcome(client, receivers_speed[client])
                else:
                    reject(client, speed)
                    debug("ERR: maximum clients reached")
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
        send_text_to_client(client,receivers_speed[client], 'bye K e e')
        del receivers[client]
        del receivers_speed[client]
