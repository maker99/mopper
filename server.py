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


class Server:
    SERVER_IP = "0.0.0.0"
    UDP_PORT = 7373
    KEEPALIVE = 10
    DEBUG = 1

    def __init__(self, server_ip=SERVER_IP, upd_port=UDP_PORT, keepalive=KEEPALIVE, dodebug=DEBUG):
        self.server_ip = server_ip
        self.udp_port = upd_port
        self.keepalive = keepalive
        self.serversock = None
        self.dodebug = dodebug

    def debug(self, str):
        if self.dodebug:
            # print str
            print("%s: %s" % (time.strftime("%Y-%m-%d %H%M%S"), str))

    def start(self):
        # connect to local hosts port 7373
        try:
            self.serversock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.serversock.bind((self.server_ip, self.udp_port))
        except:
            print("error: Port %s is already in use, maybe an earlier chatServer?" % (
                self.udp_port))
            print("try: ps xwww | grep -i chatserver")
            exit(-1)

        self.serversock.settimeout(self.keepalive)
        self.debug("Server started, listening on %s:%s" %
                   (self.server_ip, self.udp_port))

    def stop(self):
        self.serversock.close()
        self.serversock = None

    def sendto(self, ip, port, data):
        """send a data to a client 
        """
        self.serversock.sendto(data, (ip, int(port)))

    def getInput(self):
        input_bytes = None
        addr = None

        try:
            input_bytes, addr = self.serversock.recvfrom(64)
        except:
            pass

        return input_bytes, addr
