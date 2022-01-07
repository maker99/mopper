#!/usr/local/bin/python
# -*- coding: latin-1 -*-
#
# https://github.com/sp9wpn/m32_chat_server
#
# from mopp import mopp, splitmessage, debug, str2bin, str2hex, binstring2msg, string2stringmessage
from mopp import Mopp


def debugIt(m,msg):
    moppMsg = m.mopp(20, msg)
    (protocol, serialNo, wpm, data) = m.splitmessage(moppMsg)
    m.debug('message: %s -> %s(%s)' % (msg, m.str2hex(moppMsg), m.str2bin(moppMsg)))
    m.debug('protocol: %s(%s), serial: %s(%s), wpm: %s(%s), data: %s(%s)' % (
        int(protocol, 2), protocol,
        int(serialNo, 2), serialNo,
        int(wpm, 2), wpm,
        m.string2stringmessage(data), data
    ))


def smessage(m,msg):
    moppMsg = m.mopp(20, msg)
    return m.splitmessage(moppMsg)


def test_messages(m):
    assert smessage(m,'abc')[3] == '01100010010101001001100111'
    assert m.binstring2msg(smessage(m,'abc')[3]) == 'abc'
    assert m.string2stringmessage('abc') == 'abc'
    assert m.string2stringmessage('>') == ''
    assert m.string2stringmessage('A@C') == 'A@c'
    assert m.string2stringmessage('C"') == 'c'


def test_special(m):
    assert '' == m.binstring2msg('111111')
    assert '*' == m.binstring2msg('101010101010')
    assert '' == m.binstring2msg('1111101')
    assert 'en' == m.binstring2msg('01000010011')

m = Mopp()
test_messages(m)
print()
assert smessage(m,'abc')[3] == '01100010010101001001100111'
assert m.binstring2msg(smessage(m,'abc')[3]) == 'abc'
assert m.string2stringmessage('abc') == 'abc'
assert m.string2stringmessage('>') == ''
print ("%s -> %s" %('A@C',m.string2stringmessage('A@C')))
assert m.string2stringmessage('A@C') == 'A@c'
assert m.string2stringmessage('C"') == 'c'