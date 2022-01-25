import re
import logging

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)


class QsoBot:
    bot_messages = {

        'SIMPLE': {
            'QTH0'        : [r'.*(qth|loc)'                ,'my qth is aachen'     ],
            'NAME0'       : [r'.*(name|op|qrz)'            ,'my name is bot'       ],
            'RST'         : [r'.*(rst)'                    ,'ur rst is 599 5nn 5nn'],
            'WX'          : [r'.*(wx)'                     ,'wx is cloudy'         ],
            'TEMP'        : [r'.*(temp)'                   ,'temp is 5C'           ],
            'RIG'         : [r'.*(rig)'                    ,'rig is FT-857d'       ],
            'TRAIN_WORDS' : [r'.*(:w)'                     ,'rig rig rig'          ],
            'DEFAULT'     : [r'default'                    ,'?'                    ],
            'NONE'        : [r'.*'                         ,'?'                    ],
            # 'DEFAULT' : [r'default','fb hw?'],
            },
        'MED': {
            'QTH'         : [r'.*(qth|loc).*\sis\s+(\S+)'          ,'my qth is aachen'     ],
            'QTH0'        : [r'.*(qth|loc)'                        ,'qth?'                 ],
            'NAME'        : [r'.*(name|op|qrz).*is\s+(?P<OP>\S+)'  ,'dr om my name is bot' ],
            'NAME0'       : [r'.*(name|op|qrz)'                    ,'name ?'               ],
            'RST'         : [r'.*(rst).*is\s+(\S+)'                ,'ur rst is 599 5nn 5nn'],
            'RST0'        : [r'.*(rst)'                            ,'HW?'                  ],
            'WX'          : [r'.*(wx).*is\s+(\S+)'                 ,'wx is cloudy'         ],
            'WX0'         : [r'.*(wx)'                             ,'wx?'                  ],
            'TEMP'        : [r'.*(temp).*is\s+(\S+)'               ,'temp is 5C'           ],
            'TEMP0'       : [r'.*(temp)'                           ,'temp?'                ],
            'RIG'         : [r'.*(rig).*is\s+(\S+)'                ,'rig is FT-857d'       ],
            'RIG0'        : [r'.*(rig)'                            ,'rig?'                 ],
            'TRAIN_WORDS' : [r'.*(:w)'                             ,'rig rig rig'          ],
            'DEFAULT'     : [r'default'                            ,'?'                    ],
            'NONE'        : [r'.*'                                 ,'?'                    ],
            # 'DEFAULT' : [r'default','fb hw?'],
            },
        'MIDI': {
            'CALL'       : [r'(call)(\s+(hr|here|is))*\s+(?P<CALL>\S+)'    , 'dr {OP} , my call is {OWN_CALL}'           ],
            'CALL_SIMPLE': [r'(call)'                                      , 'dr om ,  my call is {OWN_CALL}'            ],
            'NAME'       : [r'(op|name|am)(\s+(hr|here|is))*\s+(?P<OP>\S+)', 'dr {OP} , my name is {OWN_NAME}'           ],
            'NAME_SIMPLE': [r'(op|name|am)'                                , 'dr om , ur name? = my name is {OWN_NAME}'  ],
            'QTH'        : [r'(loc|qth)(\s+(hr|here|is))*\s+(?P<QTH>\S+)'  , 'dr {OP} fm {QTH} , my qth is {OWN_QTH}'    ],
            'QTH_SIMPLE' : [r'(loc|qth)'                                   , 'my qth is {OWN_QTH} = ur qth?'             ],
            'WX'         : [r'(wx)(\s+(hr|here|is))*\s+(?P<WX>\S+)'        , 'wx hr is {OWN_WX}'                         ],
            'WX_SIMPLE'  : [r'(wx)'                                        , 'wx hr is {OWN_WX}'                         ],
            'TMP'        : [r'(tmp)(\s+(hr|here|is))*\s+(?P<TMP>\S+(c|f)?)', 'temp hr is {OWN_TEMP}'                     ],
            'TMP_SIMPLE' : [r'(temp)'                                      , 'temp hr is {OWN_TEMP}'                     ],
            'RIG'        : [r'(rig)(\s+(hr|here|is))*\s+(?P<RIG>\S+)'      , 'my rig is {OWN_RIG}'                       ],
            'RIG_SIMPLE' : [r'(rig)'                                       , 'my rig is {OWN_RIG}'                       ],
            'ANT'        : [r'(ant)(\s+(hr|here|is))*\s+(?P<ANT>\S+)'      , 'my ant is {OWN_ANT}'                       ],
            'ANT_SIMPLE' : [r'(ant)'                                       , 'my ant is {OWN_ANT}'                       ],
            'RST'        : [r'(rst)(\s+(is))*\s+(?P<OWN_RST>\S+)'          , 'ur rst is {UR_RST}'                        ],
            'RST_SIMPLE' : [r'(rst)'                                       , 'ur rst is {UR_RST} = dr {OP}, hw cpy?'     ],
            'GETALL2'    : [r'\?\?\?'                                      , 'wx {OWN_WX} = temp {OWN_TEMP} = rig {OWN_RIG} = ant {OWN_ANT}' ],
            'GETALL1'    : [r'\?\?'                                        , 'dr {OP} = rst {UR_RST} = qth {OWN_QTH} = name {OWN_NAME}' ],
            'REPEAT'     : [r'\?'                                          , '{LAST_MSG}'                                ],
            'DEFAULT'    : [r'.'                                           , 'dr {OP} , hw cpy?'                         ],
        }
    }

    msg_break_re = r'.*=.*'
    msg_break_char = r'='
    msg_break_in_char = r'B'       # <bk> break in char
    msg_go_ahead_char = r'N'       # <kn> go ahead

    memory_default = {
        'OP'      : 'om',
        'CALL'    : '',
        'OWN_RST' : '',
        #----------------
        'OWN_NAME': 'ger',
        'OWN_WX'  : 'sunny',
        'OWN_RIG' : 'homebrew',
        'OWN_ANT' : 'jpole',
        'OWN_TEMP': '21c',
        'OWN_QTH' : 'bristol',
        'OWN_CALL': 'm0iv',
        'UR_RST'  : '599'
    }

    
    def __init__(self) -> None:
        self.msg_buffer = ""
        self.memory = self.memory_default
        
        pass

    def extract_vars(f) -> dict:
        """extract named variables from a format string f
        """
        return {k: '' for k in re.findall(r'\{(\S+)\}', f)}


    def learn(self,new):
        for k in new.keys():
            if new[k] or k not in self.memory.keys():
                self.memory.update({k: new[k]})
        return self.memory
    
    # print a format string with values filled from a given dict
    def learn_and_answer(self, f: str, data_fields: dict) -> str:

        # create an empty dict with all formats found in the format string
        new_vars = QsoBot.extract_vars(f)
        if isinstance(new_vars, dict):
            self.learn(new_vars)
        
        # add any provided data - if we got a dict
        if isinstance(data_fields, dict):
            self.learn(data_fields)

        return(f.format(**(self.memory)))    
    
    # return a regexp match as dict or string
    def match_named_rules(pat, string: str) -> dict:
        res = {}
        r = re.search(pat, string)
        if r:
            if r.groupdict():
                res = r.groupdict()
            elif r.group():
                res = r.group()

        return res    

    # scan through a list of rules and return the name of the first matching one
    # or an emtpy list
    def match_midi_rules(rules: dict, input: str) -> list:
        
        answer = []

        for rule in rules.keys():
            # print(f'apply rule: {rule} with {rules[rule][0]}')
            res_dict = QsoBot.match_named_rules(rules[rule][0], input)
            # print (f'match_rules result: {res}')
            if len(res_dict) > 0:
                answer = [rule, res_dict]
                break

        return answer

    
    def midi_qso(self,message):
        """loops through inputs until break char is received, 
        then analyze and try to answer

        Args:
            message ([string]): [input string from remote client]
        """
        answer = []
        bot_category = 'MIDI'
        rules = self.bot_messages[bot_category]

        # append to buffer
        logging.info(f"{bot_category}_qso: message : {message}")
        self.msg_buffer += ' ' + message
        logging.info(f"{bot_category}_qso: buffer : {self.msg_buffer}")
        
        
        # extract all complete messages
        while (re.match(QsoBot.msg_break_re, self.msg_buffer) != None):
            (msg, self.msg_buffer) = self.msg_buffer.split(
                QsoBot.msg_break_char, 1)
            
            ans = ''
            (rule_name,input_fields) = QsoBot.match_midi_rules(rules, msg)
            if rule_name:   
                #input_fields=self.learn(input_fields) # learn new stuff
                answer_template = rules[rule_name][1]
                ans = self.learn_and_answer(answer_template, input_fields)

                answer.append(ans)
                logging.info("med_qso: rule: %s, answer is: %s" % (rule_name, ans))

        break_string = ' ' + QsoBot.msg_break_char + ' '
        answer_text = break_string.join(answer)
        self.learn({'LAST_MSG': answer_text})
        
        if len(answer_text) > 0:
            answer_text += ' ' + QsoBot.msg_go_ahead_char

        logging.info("med_qso: answer text is: %s" % (answer_text))
        return answer_text


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
        return self.midi_qso(message)
        # return self.med_qso(message)
        # self.simple_qso(message)
