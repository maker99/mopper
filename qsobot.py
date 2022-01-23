import re
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)


class QsoBot:
    bot_messages = {

        'SIMPLE': {
            'QTH0'        : [r'.*(qth|loc)'                ,r'my qth is aachen'     ],
            'NAME0'       : [r'.*(name|op|qrz)'            ,r'my name is bot'       ],
            'RST'         : [r'.*(rst)'                    ,r'ur rst is 599 5nn 5nn'],
            'WX'          : [r'.*(wx)'                     ,r'wx is cloudy'         ],
            'TEMP'        : [r'.*(temp)'                   ,r'temp is 5C'           ],
            'RIG'         : [r'.*(rig)'                    ,r'rig is FT-857d'       ],
            'TRAIN_WORDS' : [r'.*(:w)'                     ,r'rig rig rig'          ],
            'DEFAULT'     : [r'default'                    ,r'?'                    ],
            'NONE'        : [r'.*'                         ,r'?'                    ],
            # 'DEFAULT' : [r'default','fb hw?'],
            },
        'MED': {
            'QTH'         : [r'.*(qth|loc).*\sis\s+(\S+)'          ,r'my qth is aachen'     ],
            'QTH0'        : [r'.*(qth|loc)'                        ,r'qth?'                 ],
            'NAME'        : [r'.*(name|op|qrz).*is\s+(?P<OP>\S+)'  ,r'dr (?P<OP>) my name is bot' ],
            'NAME0'       : [r'.*(name|op|qrz)'                    ,r'name ?'               ],
            'RST'         : [r'.*(rst).*is\s+(\S+)'                ,r'ur rst is 599 5nn 5nn'],
            'RST0'        : [r'.*(rst)'                            ,r'HW?'                  ],
            'WX'          : [r'.*(wx).*is\s+(\S+)'                 ,r'wx is cloudy'         ],
            'WX0'         : [r'.*(wx)'                             ,r'wx?'                  ],
            'TEMP'        : [r'.*(temp).*is\s+(\S+)'               ,r'temp is 5C'           ],
            'TEMP0'       : [r'.*(temp)'                           ,r'temp?'                ],
            'RIG'         : [r'.*(rig).*is\s+(\S+)'                ,r'rig is FT-857d'       ],
            'RIG0'        : [r'.*(rig)'                            ,r'rig?'                 ],
            'TRAIN_WORDS' : [r'.*(:w)'                             ,r'rig rig rig'          ],
            'DEFAULT'     : [r'default'                            ,r'?'                    ],
            'NONE'        : [r'.*'                                 ,r'?'                    ],
            # 'DEFAULT' : [r'default','fb hw?'],
            }
    }

    msg_break_re = r'.*=.*'
    msg_break_char = r'='
    msg_break_in_char = r'B'       # <bk> break in char
    msg_go_ahead_char = r'N'       # <kn> go ahead

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
        bot_category = 'MED'

        # append to buffer
        logging.info("med_qso: message : %s" % message)
        self.msg_buffer += ' ' + message
        logging.info("med_qso: buffer : %s" % self.msg_buffer)
        # extract complete message
        # Todo: loop over
        while (re.match(QsoBot.msg_break_re, self.msg_buffer) != None):
            (msg, self.msg_buffer) = self.msg_buffer.split(
                QsoBot.msg_break_char, 1)
            rule = self.match_rules(msg, bot_category)
            if rule == None:
                rule = 'NONE'

            # answer.append(QsoBot.bot_messages[rule][1])
            # substitute the message with the
            answer.append(self.answer_rules(msg,rule,bot_category))
            logging.info("med_qso: rule: %s, answer is: %s" % (rule, answer))

        break_string = ' ' + QsoBot.msg_break_char + ' '
        answer_text = break_string.join(answer)
        if len(answer_text) > 0:
            answer_text += ' ' + QsoBot.msg_go_ahead_char

        logging.info("med_qso: answer text is: %s" % (answer_text))
        return answer_text

    def answer_rules(self, message, rule, category='SIMPLE'):
        answer = None

        answer = re.sub(QsoBot.bot_messages[category][rule][0],
                        QsoBot.bot_messages[category][rule][1],
                        message)

        return answer

    # match anywhere in the string
    def search_rules(self, message, category='SIMPLE'):
        answer = None

        for rule in QsoBot.bot_messages:
            if (re.search(QsoBot.bot_messages[category][rule][0], message)):
                answer = rule
                break

        return answer


    # matches only on starting of string
    def match_rules(self, message, category='SIMPLE'):
        answer = None

        for rule in QsoBot.bot_messages[category]:
            if (re.match(QsoBot.bot_messages[category][rule][0], message)):
                answer = rule
                break

        return answer

    def simple_qso(self, message):
        logging.info("simple_qso: message : %s" % message)
        answer = QsoBot.bot_messages['DEFAULT'][1]

        rule = self.match_rules(message)

        if rule != None:
            logging.info("simple_qso: message matched rule: %s" % rule)
            answer = QsoBot.bot_messages[rule][1] + QsoBot.msg_split_char
            logging.info("simple_qso: my answer is: %s" % answer)
        return answer

    def qso(self, message):
        return self.med_qso(message)
        # self.simple_qso(message)
