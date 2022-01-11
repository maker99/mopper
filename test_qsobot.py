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
#   'op here is markus',
#   'my qth is bern',
#   'qth is luzern',
#   'ur rst is 570',
#   'rst is 570',
#   'hi name here is markus']:
#    bot.qso(msg)
  
  
for msg in [
  'op here is markus =',
  'my qth', 'is', 'bern','=',
  'ur rst is 599 5nn = qth is luzern = wx ',
  'is','sunny =',
  'wx cloudy =',
  'no rule ='
  # 'ur rst is 570',
  # 'rst is 570',
  # 'hi name here is markus'
  ]:
   bot.med_qso(msg)
  
  
    

                