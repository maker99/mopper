#!/usr/local/bin/python
# -*- coding: latin-1 -*-
#
# https://github.com/sp9wpn/m32_chat_server
#
# from mopp import mopp, splitmessage, debug, str2bin, str2hex, binstring2msg, string2stringmessage
from mopp import Mopp
import logging 

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)


def debugIt(msg):
    moppMsg = Mopp.encode_text(20, msg)
    (protocol, serialNo, wpm, data) = Mopp.splitmessage(moppMsg)
    logging.debug('message: %s -> %s(%s)' %
               (msg, Mopp.str2hex(moppMsg), Mopp.str2bin(moppMsg)))
    logging.debug('protocol: %s(%s), serial: %s(%s), wpm: %s(%s), data: %s(%s)' % (
        int(protocol, 2), protocol,
        int(serialNo, 2), serialNo,
        int(wpm, 2), wpm,
        Mopp.string2stringmessage(data), data
    ))


def smessage(msg):
    moppMsg = Mopp.encode_text(20, msg)
    return Mopp.splitmessage(moppMsg)


def test_messages():
    assert smessage('abc')[3] == '01100010010101001001100111'
    assert Mopp.binstring2msg(smessage('abc')[3]) == 'abc'
    assert Mopp.string2stringmessage('abc') == 'abc'
    assert Mopp.string2stringmessage('>') == ''
    assert Mopp.string2stringmessage('A@C') == 'A@c'
    assert Mopp.string2stringmessage('C"') == 'c'


def test_special():
    assert '' == Mopp.binstring2msg('111111')
    assert '*' == Mopp.binstring2msg('101010101010')
    assert '' == Mopp.binstring2msg('1111101')
    assert 'en' == Mopp.binstring2msg('01000010011')


test_messages()
print()
assert smessage('abc')[3] == '01100010010101001001100111'
assert Mopp.binstring2msg(smessage('abc')[3]) == 'abc'
assert Mopp.string2stringmessage('abc') == 'abc'
assert Mopp.string2stringmessage('>') == ''
print("%s -> %s" % ('A@C', Mopp.string2stringmessage('A@C')))
assert Mopp.string2stringmessage('A@C') == 'A@c'
assert Mopp.string2stringmessage('C"') == 'c'

assert '' == Mopp.binstring2msg('111111')
print("%s -> %s" % ('101010101010', Mopp.binstring2msg('101010101010')))
assert '*(------)' == Mopp.binstring2msg('101010101010')
assert '' == Mopp.binstring2msg('1111101')
assert 'en' == Mopp.binstring2msg('01000010011')

msg = 'hello'
mm = Mopp.encode_text(20, msg, protocol=Mopp.PROT_V2, serial=2)
print("%s -> %s" % (msg, mm.hex(':'),))
(speed, message_text, b_protocol, b_serial_number) = Mopp.decode_message(mm)
mm = Mopp.encode_text(20, msg, protocol=Mopp.PROT_V3, serial=3)
(speed, message_text, b_protocol, b_serial_number) = Mopp.decode_message(mm)
