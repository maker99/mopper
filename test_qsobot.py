import re
import logging
from qsobot import QsoBot


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)



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
    bot2.qso(msg)

# print(bot2.memory)

# bot3 = QsoBot()
# bot4 = QsoBot()
# bot5 = QsoBot()
# bot6 = QsoBot()
# bot7 = QsoBot()
