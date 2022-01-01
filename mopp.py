#!/usr/local/bin/python
# -*- coding: latin-1 -*-
#
# https://github.com/sp9wpn/m32_chat_server
#

import time
from math import ceil


DEBUG = 1   # enable / disable debugging messages. TODO: add a logger instead and add log levels


serialNumber = 1 # TODO: make it a local var per instance: serial number for messages, increases for every encoded message

# encoding of ASCII chars to morse, represented as dit (dot) and dah (dash)
#  Note: some special chars are encoded as uppercase letters
morseCodes = { 
  "0" : "-----", 
  "1" : ".----", 
  "2" : "..---", 
  "3" : "...--", 
  "4" : "....-", 
  "5" : ".....",
  "6" : "-....", 
  "7" : "--...", 
  "8" : "---..", 
  "9" : "----.",
  "a" : ".-", 
  "b" : "-...", 
  "c" : "-.-.", 
  "d" : "-..", 
  "e" : ".", 
  "f" : "..-.", 
  "g" : "--.",
  "h" : "....", 
  "i" : "..", 
  "j" : ".---", 
  "k" : "-.-", 
  "l" : ".-..",
  "m" : "--", 
  "n" : "-.",
  "o" : "---", 
  "p" : ".--.", 
  "q" : "--.-", 
  "r" : ".-.", 
  "s" : "...", 
  "t" : "-", 
  "u" : "..-",
  "v" : "...-", 
  "w" : ".--", 
  "x" : "-..-", 
  "y" : "-.--", 
  "z" : "--..", 
  "." : ".-.-.-", 
  "," : "--..--", 
  ":" : "---...", 
  "-" : "-....-", 
  "/" : "-..-.", 
  "=" : "-...-",
  "?" : "..--..",
  "@" : ".--.-.", 
  "+" : ".-.-.", # <ar> +
  "!" : "-.-.--", 
  "'" : ".----.",
  "<err10>" : "..........",
  "<err9>" : ".........",
  "<err8>" : "........",
  "<err7>" : ".......",
  "<err6>" : "......",
  "S"      : ".-...", # <as> 45 S
  "<as>"   : ".-...", # <as> 45 S
  "A"      : "-.-.-", # <ka> 46 A
  "<ka>"   : "-.-.-", # <ka> 46 A
  "N"      : "-.--.", # <kn> 47 N
  "<kn>"   : "-.--.", # <kn> 47 N
  "K"      : "...-.-",# <sk> 48 K
  "<sk>"   : "...-.-",# <sk> 48 K
  "E"      : "...-.", # <ve> 49 E
  "<ve>"   : "...-.", # <ve> 49 E
  "ä"      : ".-.-",  # ä    50 
  "ö"      : "---.",  # ö    51
  "ü"      : "..--",  # ü    52
  "H"      : "----",   # ch   53 H
  "ch"     : "----"   # ch   53 H

}

#TODO: make this more object oriented
# e.g. we could write:   mopp.char.EOW  or mopp.prot.v1
# mopp ={

#   'char' : { 'EOW': '11', 'EOC':'00', 'DIT':'01', 'DAT':'10'},
#   'prot' : { 'NA':  '00', 'V1': '01'}
# }

# a = mopp.char.EOW




# encoding of a MOPP message, it consist of two bit elements 
#  two bit to string
moppcode = {
  "00":":", # EOC end of char
  "01":".", # dit
  "10":"-", # dah
  "11":"#"  # EOW, end of word
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

def debug(str):
  if DEBUG:
    # print str
    print( "%s: %s" % (time.strftime("%Y-%m-%d %H%M%S"), str))


# convert a string to hex format, bytes are separated by colons
def str2hex(str):
  ret = 'could not decode'
  try:
    ret=":".join("{:02x}".format(ord(c)) for c in str)
  except:
    pass

  return ret

# convert a string to hex format, bytes are separated by colons
def bytes2hex(bytes):
  ret = 'could not decode'
  try:
    ret=":".join("{:02x}".format(b) for b in bytes)
  except:
    pass

  return ret

# convert a string to a 8bit/char binary format representation, bytes/chars are not separated
def str2bin(str):
  return "".join("{:08b}".format(ord(c)) for c in str)

# convert a string to a 8bit/char binary format representation, bytes/chars are not separated
def bytes2bin(bytes):
  return "".join("{:08b}".format(b) for b in bytes)



# mopp function, creates a mopp message from speed, protocol version and a morse string
def mopp(speed,str,protocol=PROT_V1):
  global serialNumber
  global morseCodes


  m = protocol				            # protocol        2 bit
  m += bin(serialNumber)[2:].zfill(6)   # serial number   6 bit
  m += bin(speed )[2:].zfill(6)   # speed           6 bit

  for c in str:
    if c == " ":
      continue				# spaces not supported by morserino!

    try:
      if c in morseCodes:     # case of c can be lower or upper
        c = c
      elif c.lower() in morseCodes:  # uppercase char is not matching, try with the lowercase one
        c = c.lower()

      for b in morseCodes[c]:
      # for b in morseCodes[c.lower()]:
        if b == '.':
          m += DIT
        else:
          m += DAT

      m += EOC				# EOC
    except:
      debug("not found: %s" % c)
      pass  

  m = m[0:-2] + EOW			# final EOW

  m = m.ljust(int(8*ceil(len(m)/8.0)),'0')  # fill up the last byte

  res = bytearray()
  for i in range (0, len(m), 8):        # convert bin string to bytearray
    res.append(int(m[i:i+8],2))

  serialNumber = (serialNumber % 63) + 1 # step serial number and keep within 1..63

  return res





# remove the header from a byte string mopp message
def stripheader(str):
  return chr(ord(str[1]) & 3) + str[2:]  


# splits a byte string mopp message into headers and message
# the headers are binary (right aligned into a byte each)
# the message is returned as a string of 0s and 1s  
def splitmessage(msg):
  message = bytes2bin(msg)

  protocol      = message[ 0: 2]  # 2 bit     from 0
  serial_number = message[ 2: 8]  # 6 bit     from 2
  speed         = message[ 8:14]  # 6 bit     from 2+6
  data          = message[14:  ]  # the rest  from 2+6+6

  return (protocol, serial_number, speed, data)

def morse2char(morseChar):
  global morseCodes

  if morseChar == '':
    return "" 

  char='*(' + morseChar + ')'
  for c,m in morseCodes.items():
    if morseChar == m:
      char = c
  return char



# convert data encoded as a binstring (a series of 0s and 1s) into a text string 
# TODO: make robust against unknown dit/dah sequences
def binstring2msg(data):
  global moppcode

  # workaround for corrupted data strings, add 1 and EOW to make it even
  if len(data)%2 == 1:
    data = data + '111'

  # convert the moppcoded binstring into a morse code string
  morseMessage = "".join([moppcode[data[i:i+2]] for i in range(0, len(data), 2)])

  # now clean up and cut at first EOW, discard the rest, why??
  morseMessage = morseMessage.split("#")[0]

  # here we have one word, chars are separated by colons
  mchars = morseMessage.split(":")

  # decode dot - dash encoded characters into an ascii string
  message = "".join( [morse2char(mc) for mc in mchars] )
  # message=" ".join(morseMessage.split(":"))

  return message

# decode the mopp message text from the binary string message 
def string2stringmessage(string):
    moppMsg = mopp(20, string)
    (protocol, serialNo, wpm, data) = splitmessage(moppMsg)
    return binstring2msg(data)