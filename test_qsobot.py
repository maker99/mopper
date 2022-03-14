import re
import logging
from qsobot import QsoBot


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)


# class QsoBot:
# bot_messages = {
#     'QTH' : ['qth','my qth is aachen'],
#     'NAME' : ['name|op','my name is bot'],
#     'RST' : ['rst','ur rst is 599 5NN 5NN'],
#     'NAME' : ['name|op','my name is bot'],
#     'DEFAULT' : ['default','fb = hw?'],
# }

bot = QsoBot()
# for msg in [
#   'op here is dan',
#   'my qth is bern',
#   'qth is luzern',
#   'ur rst is 570',
#   'rst is 570',
#   'hi name here is marc']:
#    bot.qso(msg)


# for msg in [
#   'op here is gerd =',
#   #  'my qth', 'is',
#   #      'bern', '=',
#   # 'ur rst is 599 5nn = qth is luzern = wx ',
#   #   'is','sunny =',
#   # 'wx cloudy =',
#   # 'no rule ='
#   # 'ur rst is 570',
#   # 'rst is 570',
#   # 'hi name here is marc'
#   ]:
#    bot.med_qso(msg)

bot2 = QsoBot()

for msg in [
    'call =',
    'op =',
    'op here is dan =',
    'op here is al =',
    'op hr gard  gr rd gerd =',
    'op here is gerd x =',
    'op here is gerd sd sd =',
    'op gerd =',
    'hi name here is marc =',
    'my qth =',
    'op is gerda = my qth is bonn =',
    'wx is dipole  =',
    'temp is 10c  =',
    'temp is 0c  =',
    'temp is 1f  =',
    'temp is -20c  =',
    'temp is minus  19f  =',
    'tmp is minus  19f  =',
    'rig is ftdx 10   =',
    'ant is dipole  =',
    'rst  =',
    'ur rst is 509 =',
    '? =',
    '?? =',
    '??? =',
    'no rule =',
    # 'call is da1bc=',
    'qrs =',
    'qrz =',
    'qrq =',
]:
    bot2.midi_qso(msg)

# print(bot2.memory)

# bot3 = QsoBot()
# bot4 = QsoBot()
# bot5 = QsoBot()
# bot6 = QsoBot()
# bot7 = QsoBot()
