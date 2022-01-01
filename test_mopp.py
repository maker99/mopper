#!/usr/local/bin/python
# -*- coding: latin-1 -*-
#
# https://github.com/sp9wpn/m32_chat_server
#
from mopp import mopp, splitmessage, debug, str2bin, str2hex, binstring2msg, string2stringmessage


def debugIt(msg):
    moppMsg = mopp(20, msg)
    (protocol, serialNo, wpm, data) = splitmessage(moppMsg)
    debug('message: %s -> %s(%s)' % (msg, str2hex(moppMsg), str2bin(moppMsg)))
    debug('protocol: %s(%s), serial: %s(%s), wpm: %s(%s), data: %s(%s)' % (
        int(protocol, 2), protocol,
        int(serialNo, 2), serialNo,
        int(wpm, 2), wpm,
        string2stringmessage(data), data
    ))


def smessage(msg):
    moppMsg = mopp(20, msg)
    return splitmessage(moppMsg)


def test_messages():
    assert smessage('abc')[3] == '01100010010101001001100111'
    assert binstring2msg(smessage('abc')[3]) == 'abc'
    assert string2stringmessage('abc') == 'abc'
    assert string2stringmessage('>') == ''
    assert string2stringmessage('A@C') == 'A@c'
    assert string2stringmessage('C"') == 'c'


def test_special():
    assert '' == binstring2msg('111111')
    assert '*' == binstring2msg('101010101010')
    assert '' == binstring2msg('1111101')
    assert 'en' == binstring2msg('01000010011')

test_messages
print()
assert smessage('abc')[3] == '01100010010101001001100111'
assert binstring2msg(smessage('abc')[3]) == 'abc'
assert string2stringmessage('abc') == 'abc'
assert string2stringmessage('>') == ''
print ("%s -> %s" %('A@C',string2stringmessage('A@C')))
assert string2stringmessage('A@C') == 'A@c'
assert string2stringmessage('C"') == 'c'