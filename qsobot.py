from os import urandom
import re
import logging
import random

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
            'CALL'       : [r'\b(call)\b.*\b(?P<CALL>\S+)\b'        , 'dr {OP} , my call is {OWN_CALL} {OWN_CALL} {OWN_CALL}'             ],
            'CALL_SIMPLE': [r'\b(call)\b'                           , 'dr om ,  my call is {OWN_CALL} {OWN_CALL} {OWN_CALL}'              ],
            'NAME'       : [r'\b(op|name|am)\b.*\b(?P<OP>\w{3,})\b' , 'dr {OP} , my name is {OWN_NAME} {OWN_NAME} {OWN_NAME}'             ],
            'NAME_SIMPLE': [r'\b(op|name|am)\b'                     , 'dr om , ur name? = my name is {OWN_NAME} {OWN_NAME} {OWN_NAME}'    ],
            'QTH'        : [r'\b(loc|qth)\b.*\b(?P<QTH>\w{3,})\b'   , 'dr {OP} fm {QTH} , my qth is {OWN_QTH} {OWN_QTH} {OWN_QTH}'        ],
            'QTH_SIMPLE' : [r'\b(loc|qth)\b'                        , 'my qth is {OWN_QTH} {OWN_QTH} {OWN_QTH} = ur qth?'                 ],
            'WX'         : [r'\b(wx)\b.*\b(?P<WX>\w{3,})\b'         , 'wx hr is {OWN_WX} {OWN_WX} {OWN_WX}'                               ],
            'WX_SIMPLE'  : [r'\b(wx)\b'                             , 'wx hr is {OWN_WX} {OWN_WX} {OWN_WX}'                               ],
            'TMP'        : [r'\b(tmp|temp)\b.*\b(?P<TMP>(-|\+|minus|plus\s*)?\w+\s*(c|f)?)\b' , 'temp hr is {OWN_TEMP} {OWN_TEMP} {OWN_TEMP}'                       ],
            'TMP_SIMPLE' : [r'\b(tmp|temp)\b'                       , 'temp hr is {OWN_TEMP} {OWN_TEMP} {OWN_TEMP}'                       ],
            'RIG'        : [r'\b(rig)\b.*\b(?P<RIG>\w{3,})\b'       , 'my rig is {OWN_RIG} {OWN_RIG} {OWN_RIG}'                           ],
            'RIG_SIMPLE' : [r'\b(rig)\b'                            , 'my rig is {OWN_RIG} {OWN_RIG} {OWN_RIG}'                           ],
            'ANT'        : [r'\b(ant)\b.*\b(?P<ANT>\w{3,})\b'       , 'my ant is {OWN_ANT} {OWN_ANT} {OWN_ANT}'                           ],
            'ANT_SIMPLE' : [r'\b(ant)\b'                            , 'my ant is {OWN_ANT} {OWN_ANT} {OWN_ANT}'                           ],
            'RST'        : [r'\b(rst)\b.*\b(?P<OWN_RST>\w{3,})\b'   , 'ur rst is {UR_RST} {UR_RST} {UR_RST}'                              ],
            'RST_SIMPLE' : [r'\b(rst)\b'                            , 'ur rst is {UR_RST} {UR_RST} {UR_RST} = dr {OP} , hw cpy?'          ],
            'GETALL2'    : [r'\?\?\?'                               , 'wx {OWN_WX} {OWN_WX} = temp {OWN_TEMP} {OWN_TEMP} = rig {OWN_RIG} {OWN_RIG} = ant {OWN_ANT} {OWN_ANT}' ],
            'GETALL1'    : [r'\?\?'                                 , 'dr {OP} = rst {UR_RST} {UR_RST} = qth {OWN_QTH} {OWN_QTH} = name {OWN_NAME} {OWN_NAME}' ],
            'REPEAT'     : [r'\?'                                   , '{LAST_MSG}'                                                        ],
            'QRS'        : [r'qrs'                                  , 'slower'                                                        ],
            'QRQ'        : [r'qrq'                                  , 'faster'                                                        ],
            'QRZ'        : [r'qrz'                                  , '{OWN_CALL} {OWN_CALL} {OWN_CALL}'                                                        ],
            'DEFAULT'    : [r'.'                                    , 'dr {OP} , hw cpy?'                                                 ],
        }
    }

    msg_break_re      = r'.*=.*'
    msg_break_char    = r'='
    msg_break_in_char = r'B'       # <bk> break in char
    msg_go_ahead_char = r'N'       # <kn> go ahead


    def __init__(self) -> None:
        memory_default = {
            'OP'      : 'om',
            'CALL'    : '',
            'OWN_RST' : '',
            #----------------
            'OWN_NAME': 'ann,bea,ali,ake,bee,bot,buzz,bat,len,han,ted,zoe,may,april,fan,fran,ger,dan,rob,tom,fred,hans,gerd,bob,will,fritz,jan,alan,adam,andre,bert,ben,tim,ken,marc,matt,tom,val,zoe,gill,',
            'OWN_WX'  : 'sunny, cloudy ,rainy,foggy,snowy,windy,chilly,',
            'OWN_RIG' : 'qrp, homebrew,ic 7300,ic705,ftdx10',
            'OWN_ANT' : 'jpole,dipole,random,kelemen,endfed,gp,hb9cv,trap dipole,flagpole,vertical,',
            'OWN_TEMP': 'minus 10c, 0c, 5c, 21c,31c',
            'OWN_QTH' : 'bristol,kent,london,aachen,wuerselen,simmerath,brand,kiev,herzogenrath,bonn,koeln,cologne,bern,hamburg,',
            'OWN_CALL': 'm0iv,da1bc,db2cd,dd3ef,de4fg,ia3tv',
            'UR_RST'  : '599,509,518,579,589',
            'SPEED_DIFF'  : '0',
        }

    
        self.msg_buffer = ""
        self.memory = {}
        choosen = QsoBot.random_choice(memory_default)
        self.learn(choosen)
        logging.info(f"QsoBot: init : {choosen}")
        # logging.info(f"QsoBot: init : {self.memory}")


    def extract_vars(f) -> dict:
        """extract named variables from a format string f
        """
        return {k: '' for k in re.findall(r'\{(\S+)\}', f)}
    
    def split_and_clean(input: str) -> list:
        """split a string with commata and clean the results

        Args:
            input (str): [description]

        Returns:
            cleaned list: [description]
        """        
        logging.debug(f"split_and_clean: {input}")
        return [x.strip() for x in input.split(',') if x.strip()]


    def random_choice(op_data: dict) -> dict:
        the_choosen = {}
        for k in op_data.keys():
            strings = QsoBot.split_and_clean(op_data[k])
            if len(strings) > 0:
                val = random.choice(strings)
                the_choosen.update({k: val})
        return the_choosen    


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
        answer_text = ''
        bot_category = 'MIDI'
        rules = self.bot_messages[bot_category]
        BREAK = ' ' + QsoBot.msg_break_char + ' '
        END_CHAR = QsoBot.msg_go_ahead_char        

        # append to buffer
        logging.info(f"{bot_category}_qso: message : {message}")
        self.msg_buffer += ' ' + message
        logging.info(f"{bot_category}_qso: buffer : {self.msg_buffer}")
        
        
        # extract all complete messages
        while (re.match(QsoBot.msg_break_re, self.msg_buffer) != None):
            (msg, self.msg_buffer) = self.msg_buffer.split(
                QsoBot.msg_break_char, 1)
            
            if len(msg) > 0:
                
                ans = ''
                (rule_name,input_fields) = QsoBot.match_midi_rules(rules, msg)
                
                if rule_name:   
                    #input_fields=self.learn(input_fields) # learn new stuff
                    answer_template = rules[rule_name][1]
                    ans = self.learn_and_answer(answer_template, input_fields)

                    if len(ans) > 0:
                        answer.append(ans)
                        logging.info("med_qso: rule: %s, answer is: %s" % (rule_name, ans))

        if len(answer) > 0:
            answer_text = BREAK.join(answer)
            self.learn({'LAST_MSG': answer_text})
        
        if len(answer_text) > 0:
            answer_text += ' ' + END_CHAR

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
