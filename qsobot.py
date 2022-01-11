import re
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

class QsoBot:
    bot_messages = {
        'QTH'         : [r'.*(qth|loc).*\sis\s+(\S+)'  ,'my qth is aachen'     ],
        'QTH0'        : [r'.*(qth|loc)'                ,'qth?'                 ],
        'NAME'        : [r'.*(name|op|qrz).*is\s+(\S+)','dr %s my name is bot' ],
        'NAME0'       : [r'.*(name|op|qrz)'            ,'name ?'               ],
        'RST'         : [r'.*(rst).*is\s+(\S+)'        ,'ur rst is 599 5nn 5nn'],
        'RST0'        : [r'.*(rst)'                    ,'HW?'                  ],
        'WX'          : [r'.*(wx).*is\s+(\S+)'         ,'wx is cloudy'         ],
        'WX0'         : [r'.*(wx)'                     ,'wx?'                  ],
        'TEMP'        : [r'.*(temp).*is\s+(\S+)'       ,'temp is 5C'           ],
        'TEMP0'       : [r'.*(temp)'                   ,'temp?'                ],
        'RIG'         : [r'.*(rig).*is\s+(\S+)'        ,'rig is FT-857d'       ],
        'RIG0'        : [r'.*(rig)'                    ,'rig?'                 ],
        'TRAIN_WORDS' : [r'.*(:w)'                     ,'rig rig rig'          ],
        'DEFAULT'     : [r'default'                    ,'?'                    ],
        'NONE'        : [r'.*'                         ,'?'                    ],
        # 'DEFAULT' : [r'default','fb hw?'],
    }
    
    msg_split_re = r'.*=.*'
    msg_split_char = r'='
    msg_break_in_char = r'B'   # <bk> break in char
    
    def __init__(self) -> None:
        self.msg_buffer = ""
        pass
        
    def med_qso(self, message):
        """loops through inputs until break char is received, 
        then analyze and try to answer

        Args:
            message ([string]): [input string from remote client]
        """        
        answer = []
        # append to buffer
        logging.info("med_qso: message : %s" % message)
        self.msg_buffer += ' ' + message
        logging.info("med_qso: buffer : %s" % self.msg_buffer)
        # extract complete message
        #Todo: loop over 
        while ( re.match(QsoBot.msg_split_re,self.msg_buffer) != None ):
            (msg,self.msg_buffer) = self.msg_buffer.split(QsoBot.msg_split_char,1)
            rule = self.match_rules(msg)
            if rule == None:
                rule = 'NONE'
                
            answer.append(QsoBot.bot_messages[rule][1])
            logging.info("med_qso: rule: %s, answer is: %s" % (rule,answer))
                
            
        answer_text = QsoBot.msg_split_char.join(answer)
        if len(answer_text  ) > 0:
            answer_text += QsoBot.msg_break_in_char
            
        logging.info("med_qso: answer text is: %s" % (answer_text))
        return answer_text
        
    def match_rules(self, message):
        answer = None
        
        for rule in QsoBot.bot_messages:
            if (re.match(QsoBot.bot_messages[rule][0],message)):
                answer = rule
                break
        
        return answer
    
    def simple_qso(self,message):
        logging.info("simple_qso: message : %s" % message)
        answer = QsoBot.bot_messages['DEFAULT'][1]
        
        rule = self.match_rules(message)
        
        if rule != None:
            logging.info("simple_qso: message matched rule: %s" % rule)
            answer = QsoBot.bot_messages[rule][1] + QsoBot.msg_split_char
            logging.info("simple_qso: my answer is: %s" % answer)
        return answer
        
    
                
    def qso(self,message):
        return self.med_qso(message)
        # self.simple_qso(message)
        