import re
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

class QsoBot:
    bot_messages = {
        'QTH' : [r'.*(qth|loc).*is\s+(\S+)','my qth is aachen'],
        'NAME' : [r'.*(name|op|qrz).*is\s+(\S+)','dr %s my name is bot'],
        'RST' : [r'.*(rst)','ur rst is 599 5nn 5nn'],
        'WX' : [r'.*(wx)','wx is cloudy'],
        'TEMP' : [r'.*(temp)','temp is 5C'],
        'RIG' : [r'.*(rig)','rig is FT-857D'],
        'DEFAULT' : [r'default','?'],
        # 'DEFAULT' : [r'default','fb hw?'],
    }
    
    def qso(self,message):
        logging.info("qso_bot: message is: %s" % message)
        answer = QsoBot.bot_messages['DEFAULT'][1]
        # message = message.lower()
        
        for rule in QsoBot.bot_messages:
            if (re.match(QsoBot.bot_messages[rule][0],message)):
                logging.info("qso_bot: message matched rule: %s" % rule)
                answer = QsoBot.bot_messages[rule][1] + ' ='
                break
        logging.info("my answer is: %s" % answer)
        return answer
                