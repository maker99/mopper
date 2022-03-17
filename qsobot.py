from os import urandom
import re
import logging
import random
import jinja2

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)


class QsoBot:
    bot_messages = {
        'macros' : { 
            'DEFAULT' : """
                {%- macro REP(_MYVAL,_REPEAT) -%} 
                    {{- _MYVAL| R(_REPEAT or RPT) -}} 
                {%- endmacro -%}
                
                {%- macro RND(_LIST) -%}
                    {{ _LIST | random }}
                {%- endmacro -%}
                    
                {%- macro GREETING(_TIME) -%}
                    {{_TIME or "gd"}} dr {{OM or "om"}} es {{RND(['tnx','tks'])}} {{RND(['fer','fr'])}} the call
                {%- endmacro -%}
                        
                {%- macro UR(_RST,_REPEAT) -%}
                    ur rst {{ RND(['is ', '']) }}{{ REP(_RST or "599",_REPEAT or RPT)}}
                {%- endmacro -%}
                    
                {%- macro FM_QTH() -%}
                    {%- if QTH -%}
                        fm {{QTH}}
                    {%- else -%}
                        , ur qth?
                    {%- endif -%}
                {%- endmacro -%}
                
                {%- macro WHAT_RST() -%}
                    {%- if not OWN_RST -%}
                        = hw cpy?
                    {%- endif -%}
                {%- endmacro -%}
                    
                {%- macro ANS(_MYVAR,_VAL,_REPEAT) -%}
                    {{ RND(['the ', 'my ', ' ']) }}{{ _MYVAR }} {{ RND(['hr is ', 'is ','hr ', '']) }}{{ REP(_VAL or "nice",_REPEAT or RPT)}}
                {%- endmacro -%}
                
                {%- macro DR_OP() -%}
                    dr {{OP|default('om')}} 
                {%- endmacro -%}
                               
                {%- macro CALL() -%}
                    {{DR_OP()}} my call is {{5|S()}}{{REP(OWN_CALL)}} {{0|S()}}
                {%- endmacro -%}
            """
        },
        'MIDI': {
            'CALL'       : [r'\b(call)\b(.*\b(?P<CALL>\S+)\b)?'        , '{{CALL()}}'],
            'NAME'       : [r'\b(op|name|am)\b(.*\b(?P<OP>\w{3,})\b)?' , '{{DR_OP()}} my name is {{REP(OWN_NAME)}}'                    ],
            'QTH'        : [r'\b(loc|qth)\b(.*\b(?P<QTH>\w{3,})\b)?'   , '{{DR_OP()}} {{FM_QTH()}} = my qth is {{REP(OWN_QTH)}}'       ],
            'WX'         : [r'\b(wx)\b(.*\b(?P<WX>\w{3,})\b)?'         , 'wx hr is {{REP(OWN_WX)}}'                                  ],
            'TMP'        : [r'\b(tmp|temp)\b(.*\b(?P<TMP>(-|\+|minus|plus\s*)?\w+\s*(c|f)?)\b)?' , 'temp hr is {{REP(OWN_TEMP)}}'    ],
            'RIG'        : [r'\b(rig)\b(.*\b(?P<RIG>\w{3,})\b)?'       , 'my rig is {{REP(OWN_RIG)}}'                                ],
            'ANT'        : [r'\b(ant)\b(.*\b(?P<ANT>\w{3,})\b)?'       , 'my ant is {{REP(OWN_ANT)}}'                                ],
            'RST'        : [r'\b(rst)\b(.*\b(?P<OWN_RST>\w{3,})\b)?'   , 'ur rst is {{REP(UR_RST)}} {{WHAT_RST()}}'                  ],
            'GETALL2'    : [r'\?\?\?'                                  , 'wx {{REP(OWN_WX)}} = temp {{REP(OWN_TEMP)}} = rig {{REP(OWN_RIG)}} = ant {{REP(OWN_ANT)}}' ],
            'GETALL1'    : [r'\?\?'                                    , '{{DR_OP()}} = rst {{REP(UR_RST)}} = qth {{REP(OWN_QTH)}} = name {{REP(OWN_NAME)}}' ],
            'REPEAT'     : [r'\?'                                      , '{{LAST_MSG}}'                                              ],
            'QRS'        : [r'qrs'                                     , 'slower'                                                    ],
            'QRQ'        : [r'qrq'                                     , 'faster'                                                    ],
            'QRZ'        : [r'qrz'                                     , '{{OWN_CALL | R(RPT)}}'                                     ],
            'DEFAULT'    : [r'.'                                       , '{{DR_OP()}} , hw cpy?'                                       ],
        }
    }

    msg_break_re      = r'.*=.*'
    msg_break_char    = r'='
    msg_break_in_char = r'B'       # <bk> break in char
    msg_go_ahead_char = r'N'       # <kn> go ahead


    def __init__(self) -> None:
        """
        init a new bot
            each bot has it's own characteristics, 
                for example: name, call, qth,...
                and can remember those data sent by the remote op
            this allows to answer on data the bot received or to ask for 
                data not yet received
            using jinja2 and some filters allows to create different answers based on
                randomly chosing from a set of answer strings.
        """        
        
        # the 
        bot_characteristics = {
            'OP'      : 'om',
            'CALL'    : '',
            'OWN_RST' : '',
            #----------------
            'OWN_NAME': 'ann,bea,ali,ake,bee,bot,buzz,bat,len,han,ted,zoe,may,april,fan,fran,ger,dan,rob,tom,fred,hans,gerd,bob,will,fritz,jan,alan,adam,andre,bert,ben,tim,ken,marc,matt,tom,val,zoe,gill,',
            'OWN_WX'  : 'sunny, cloudy ,rainy,foggy,snowy,windy,chilly,',
            'OWN_RIG' : 'qrp, homebrew,ic 7300,ic705,ftdx10',
            'OWN_ANT' : 'jpole,dipole,random,kelemen,endfed,gp,hb9cv,trap dipole,flagpole,vertical,',
            'OWN_TEMP': 'minus 10c, 0c, 5c, 21c,31c',
            'OWN_QTH' : 'bristol,kent,london,aachen,wuerselen,simmerath,brand,kiev,herzogenrath,bonn,koeln,cologne,bern,hamburg,pley',
            'OWN_CALL': 'm0iv,da1bc,db2cd,dd3ef,de4fg,ia3tv',
            'UR_RST'  : '599,509,518,579,589',
            'SPEED'   : '20', # allows to select a different defaults speed than remote op
            'SPEED_DIFF'  : '0', # allows to select a different defaults speed than remote op
            'RPT'     : '3',
        }

    
        self.msg_buffer = ""
        self.memory = {}
        choosen_bot = QsoBot.mix_an_op(bot_characteristics)
        self.learn(choosen_bot)
        
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
        
        logging.info(f"QsoBot: init : {choosen_bot}")
        # logging.info(f"QsoBot: init : {self.memory}")
        
        # init jinja2 environment and add filters
        self.j2env = jinja2.Environment()
        self.j2env.filters["R"] = self.j2_repeat_filter
        self.j2env.filters["S"] = self.j2_speed_setter_relative
        self.j2env.filters["A"] = self.j2_speed_setter_absolute


    def render(self, f):
        macros = self.bot_messages['macros']['DEFAULT']
        answer = self.j2env.from_string(macros+f).render(self.memory)
        p = re.compile('\s+' )
        answer = p.sub(' ', answer) 
        return answer   
        
        
    def j2_repeat_filter(self,value, repeat=1):
        """
       Jinja2 filter - repeat the input value several times, joined with spaces

        repeat value defaults to 1

        :param value: string to be repeated
        :param repeat: repetition
        :return: string
        """

        return ' '.join([str(value)] * int(repeat))
    
    
    def j2_speed_setter_relative(self,speed_diff: int = 9999):
        """
        jinja2 filter to set relative cw speed 
        :param value: value to be repeated
        :param repeat: how often to repeat
        :return: string
        """
        self.memory['SPEED_DIFF'] = speed_diff
        logging.debug(f"j2_speed_setter_relative: {self.memory['SPEED_DIFF']}")
        
        return ''


    def j2_speed_setter_absolute(self,speed: int = 9999):
        """
        jinja2 filter to set relative cw speed 
        :param value: value to be repeated
        :param repeat: how often to repeat
        :return: string
        """
        if speed == 0 :
            self.memory['SPEED_DIFF'] = 0
        else:
            self.memory['SPEED_DIFF'] = speed - self.memory['SPEED_DIFF']
        logging.debug(f"jinja2 filter to set relative cw speed: {self.memory['SPEED_DIFF']}")
        
        return ''


    def extract_vars(f) -> dict:
        """extract named variables from a format string f

        """
        return {k: '' for k in re.findall(r'\{(\S+)\}', f)}
    
    
    def split_and_strip(input: str) -> list:
        """split a string at commata and strip leading and trailing spaces

        Args:
            input (str): [description]

        Returns:
            cleaned list: [description]
        """        
        logging.debug(f"split_and_clean: {input}")
        return [x.strip() for x in input.split(',') if x.strip()]


    def mix_an_op(op_data: dict) -> dict:
        """select and return random values for all op's characteristics
            for example: name, call, rig, ant, qth, ...
            
        Args:
            op_data (dict): a list of characteristics for ops

        Returns:
            dict: one randomly chosen value for each characteristic
        """        
        the_choosen_op = {}
        for k in op_data.keys():
            strings = QsoBot.split_and_strip(op_data[k])
            if len(strings) > 0:
                val = random.choice(strings)
                the_choosen_op.update({k: val})
        return the_choosen_op    


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
        answer =  self.render(f)
        return answer 


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
    def match_rules(rules: dict, input: str) -> list:
        
        answer = []

        for rule in rules.keys():
            # print(f'apply rule: {rule} with {rules[rule][0]}')
            res_dict = QsoBot.match_named_rules(rules[rule][0], input)
            # print (f'match_rules result: {res}')
            if len(res_dict) > 0:
                answer = [rule, res_dict]
                break

        return answer

    
    def qso(self,message):
        """conduct a qso based on input from the remote op
        how it works:
        loop through input and split it into segments based on the break char
         
            analyze each segment
                match it to the given rules, e.g. OP, QTH, WX, ... 
                extract values (e.g. name, qth, rst, ... ) and remember them
                and answer the segment
                
        over time we collect more details and can put these into our answers   
            for example: when we know the name we can replease 'om' in 'dr om' by the op's name

        Args:
            message ([string]): [input string from remote operator]
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
                (rule_name,input_fields) = QsoBot.match_rules(rules, msg)
                
                if rule_name:   
                    #input_fields=self.learn(input_fields) # learn new stuff
                    answer_template = rules[rule_name][1]
                    ans = self.learn_and_answer(answer_template, input_fields)

                    if len(ans) > 0:
                        answer.append(ans)
                        logging.info("qso: rule: %s, answer is: %s" % (rule_name, ans))

        if len(answer) > 0:
            answer_text = BREAK.join(answer)
            self.learn({'LAST_MSG': answer_text})
        
        if len(answer_text) > 0:
            answer_text += ' ' + END_CHAR

        # remove leading and trailing whitepspace and
        # shrink all white space to single spaces one
        answer_text = answer_text.strip()
        answer_text = ' '.join(answer_text.split())
        
        logging.info("qso: answer text is: %s" % (answer_text))
        return answer_text

