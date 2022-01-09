#!/usr/local/bin/python
# -*- coding: latin-1 -*-
#
# an implementation of the mopp protocol for Morserino-32
# based on https://github.com/sp9wpn/m32_chat_server
# the protocol description is:  https://github.com/oe1wkl/Morserino-32/blob/master/Documentation/Protocol%20Description/morse_code_over_packet_protocol.md
#

import time
from math import ceil


class Mopp:

    DEBUG = 1
    # encoding of ASCII chars to morse, represented as dit (dot) and dah (dash)
    #  Note: some special chars are encoded as uppercase letters
    morseCodes = {
        "0": "-----",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        "a": ".-",
        "b": "-...",
        "c": "-.-.",
        "d": "-..",
        "e": ".",
        "f": "..-.",
        "g": "--.",
        "h": "....",
        "i": "..",
        "j": ".---",
        "k": "-.-",
        "l": ".-..",
        "m": "--",
        "n": "-.",
        "o": "---",
        "p": ".--.",
        "q": "--.-",
        "r": ".-.",
        "s": "...",
        "t": "-",
        "u": "..-",
        "v": "...-",
        "w": ".--",
        "x": "-..-",
        "y": "-.--",
        "z": "--..",
        ".": ".-.-.-",
        ",": "--..--",
        ":": "---...",
        "-": "-....-",
        "/": "-..-.",
        "=": "-...-",
        "?": "..--..",
        "@": ".--.-.",
        "+": ".-.-.",  # <ar> +
        "!": "-.-.--",
        "'": ".----.",
        "<err10>": "..........",
        "<err9>": ".........",
        "<err8>": "........",
        "<err7>": ".......",
        "<err6>": "......",
        "S": ".-...",  # <as> 45 S
        "<as>": ".-...",  # <as> 45 S
        "A": "-.-.-",  # <ka> 46 A
        "<ka>": "-.-.-",  # <ka> 46 A
        "N": "-.--.",  # <kn> 47 N
        "<kn>": "-.--.",  # <kn> 47 N
        "K": "...-.-",  # <sk> 48 K
        "<sk>": "...-.-",  # <sk> 48 K
        "E": "...-.",  # <ve> 49 E
        "<ve>": "...-.",  # <ve> 49 E
        "ä": ".-.-",  # ä    50
        "ö": "---.",  # ö    51
        "ü": "..--",  # ü    52
        "H": "----",   # ch   53 H
        "ch": "----"   # ch   53 H

    }

    # TODO: make this more object oriented
    # e.g. we could write:   mopp.char.EOW  or mopp.prot.v1
    # mopp ={

    #   'char' : { 'EOW': '11', 'EOC':'00', 'DIT':'01', 'DAT':'10'},
    #   'prot' : { 'NA':  '00', 'V1': '01'}
    # }

    # a = mopp.char.EOW

    # encoding of a MOPP message, it consist of two bit elements
    #  two bit to string
    moppcode = {
        "00": ":",  # EOC end of char
        "01": ".",  # dit
        "10": "-",  # dah
        "11": "#"  # EOW, end of word
    }

    # MOPP char to bits
    EOW = "11"
    EOC = "00"
    DIT = "01"
    DAT = "10"

    # constants for the MOPP protocol field
    PROT_V1 = "01"
    PROT_V2 = "10"
    PROT_V3 = "11"

    def enable_debug():
        Mopp.DEBUG = 1

    def disable_debug():
        Mopp.DEBUG = 0

    def debug(str):
        if Mopp.DEBUG:
            # print str
            print("%s: %s" % (time.strftime("%Y-%m-%d %H%M%S"), str))

    # convert a string to hex format, bytes are separated by colons

    def str2hex(str):
        ret = 'could not decode'
        try:
            ret = ":".join("{:02x}".format(ord(c)) for c in str)
        except:
            pass

        return ret

    # convert a string to hex format, bytes are separated by colons

    def bytes2hex(bytes):
        ret = 'could not decode'
        try:
            ret = ":".join("{:02x}".format(b) for b in bytes)
        except:
            pass

        return ret

    # convert a string to a 8bit/char binary format representation, bytes/chars are not separated

    def str2bin(str):
        return "".join("{:08b}".format(ord(c)) for c in str)

    # convert a string to a 8bit/char binary format representation, bytes/chars are not separated

    def bytes2bin(bytes):
        return "".join("{:08b}".format(b) for b in bytes)

    def normalize_serial(serial):
        return int(int(serial) % 63)

    def increment_serial(serial):
        return int((int(serial) + 1) % 63)

    # mopp function, creates a mopp message from speed, protocol version and a morse string

    def encode_text(speed, text, protocol=None, serial=1):

        if protocol == None:
            protocol = Mopp.PROT_V1

        serial = Mopp.normalize_serial(serial)

        m = protocol				        # protocol        2 bit
        m += bin(serial)[2:].zfill(6)       # serial number   6 bit
        m += bin(int(speed))[2:].zfill(6)   # speed           6 bit

        for c in text:
            if c == " ":
                continue				# spaces not supported by morserino!

            try:
                if c in Mopp.morseCodes:     # case of c can be lower or upper
                    c = c
                elif c.lower() in Mopp.morseCodes:  # uppercase char is not matching, try with the lowercase one
                    c = c.lower()

                for b in Mopp.morseCodes[c]:
                    # for b in Mopp.morseCodes[c.lower()]:
                    if b == Mopp.moppcode[Mopp.DIT]:
                        m += Mopp.DIT
                    else:
                        m += Mopp.DAT

                m += Mopp.EOC				# EOC
            except:
                Mopp.debug("not found: %s" % c)
                pass

        m = m[0:-2] + Mopp.EOW			# final EOW

        m = m.ljust(int(8*ceil(len(m)/8.0)), '0')  # fill up the last byte

        res = bytearray()
        for i in range(0, len(m), 8):        # convert bin string to bytearray
            res.append(int(m[i:i+8], 2))

        return res

    # remove the header from a byte string mopp message

    def stripheader(str):
        return chr(ord(str[1]) & 3) + str[2:]

    def splitmessage(msg):
        """ splits a byte string mopp message into headers and message
            the headers are binary (right aligned into a byte each)
            the message is returned as a string of 0s and 1s  
        """
        # TODO: implement error handling and logging
        message = Mopp.bytes2bin(msg)

        protocol = message[0: 2]  # 2 bit     from 0
        serial_number = message[2: 8]  # 6 bit     from 2
        speed = message[8:14]  # 6 bit     from 2+6
        data = message[14:]  # the rest  from 2+6+6

        return (protocol, serial_number, speed, data)

    def decode_message(input_bytes):
        """ get data from a mopp message:
            speed, text, protocol and serial number
        """
        # TODO: implement error handling and logging

        (b_protocol, b_serial_number, b_speed,
         b_data) = Mopp.splitmessage(input_bytes)
        speed = int(b_speed, 2)
        message_text = Mopp.binstring2msg(b_data)

        Mopp.debug('==============')
        Mopp.debug('"%s" -> %s' %
                   (Mopp.bytes2bin(input_bytes), input_bytes.hex(':')))
        Mopp.debug('--- Header ---')
        Mopp.debug('%s             = protocol version: %s' %
                   (b_protocol, int(b_protocol, 2)))
        Mopp.debug('  %s       = serial number   : %s' %
                   (b_serial_number, int(b_serial_number, 2)))
        Mopp.debug('        %s = speed           : %s wpm' %
                   (b_speed, int(b_speed, 2)))
        Mopp.debug('--- Data ---')
        Mopp.debug('%s = "%s"' % (b_data, message_text))
        Mopp.debug('==============')

        return (speed, message_text, b_protocol, b_serial_number)

    # get_message = decode_message

    def morse2char(morseChar):

        if morseChar == '':
            return ""

        char = '*(' + morseChar + ')'
        for c, m in Mopp.morseCodes.items():
            if morseChar == m:
                char = c
                break
        return char

    # convert data encoded as a binstring (a series of 0s and 1s) into a text string
    # TODO: make robust against unknown dit/dah sequences

    def binstring2msg(data):

        # workaround for corrupted data strings, add 1 and EOW to make it even
        if len(data) % 2 == 1:
            data = data + '111'

        # convert the moppcoded binstring into a morse code string
        morseMessage = "".join([Mopp.moppcode[data[i:i+2]]
                                for i in range(0, len(data), 2)])

        # now clean up and cut at first EOW, discard the rest, why??
        morseMessage = morseMessage.split(Mopp.moppcode[Mopp.EOW])[0]

        # here we have one word, chars are separated by colons
        mchars = morseMessage.split(Mopp.moppcode[Mopp.EOC])

        # decode dot - dash encoded characters into an ascii string
        message = "".join([Mopp.morse2char(mc) for mc in mchars])
        # message=" ".join(morseMessage.split(":"))

        return message

    # decode the mopp message text from the binary string message

    def string2stringmessage(string):
        moppMsg = Mopp.encode_text(20, string)
        (protocol, serialNo, wpm, data) = Mopp.splitmessage(moppMsg)
        return Mopp.binstring2msg(data)
