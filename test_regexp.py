import re

def extract_vars(f) -> dict:
    """extract named variables from a format string f
    """
    return {k: '' for k in re.findall(r'\{(\S+)\}', f)}

# default data for dataset
defaults = {
    'OP': 'dr om',
    'CALL': '',
    'OWN_NAME': 'Ger',
    'OWN_QTH': 'Bristol',
    'OWN_CALL': 'M0iv'
}

# update a dict:
#  add new key value pairs and
#  update values when the key already exists
#  this will not delete a value with an empty one


def learn(old, new):
    r = old
    for k in new.keys():
        if new[k] or k not in old.keys():
            r.update({k: new[k]})
    return r

# print a format string with values filled from a given dict
def apply_format(f: str, data_fields: dict) -> str:

    # create an empty dict with all formats found in the format string
    data = extract_vars(f)
    data.update(defaults)  # update with default (already known values)
    # add any provided data - if we got a dict

    if isinstance(data_fields, dict):
        data.update(data_fields)

    return(f.format(**data))


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
        res_dict = match_named_rules(rules[rule][0], input)
        # print (f'match_rules result: {res}')
        if len(res_dict) > 0:
            answer = [rule, res_dict]
            break

    return answer


# take input string, search for a matching rule and use the rule's format 
# string to create an answer 
# use the rules' match data found in the input
def answer_it(rules: object, input: str) -> str:
    answer = ''
    found_rule = match_rules(rules, input)
    if found_rule:    
        answer = apply_format(rules[found_rule[0]][1], found_rule[1])
        
    return answer


rules = {
    'OP':         [r'(op|name|am)\s+((hr|is)+\s+)*(?P<OP>\S+)', 'hi there {OP}, my name is {OWN_NAME}',    ['op?', 'ur name pse?', 'dr om what is ur name?']],
    'OP_SIMPLE':  [r'(op|name|am)',                             'dr om, ur name? = my name is {OWN_NAME}', ['op?', 'ur name pse?', 'dr om what is ur name?']],
    'QTH':        [r'(loc|qth)(\s+(hr|is))*\s+(?P<QTH>\S+)',    '{OP} fm {QTH}, my qth is {OWN_QTH}',      ['qth?', 'ur qth pse', 'what is ur qth?']],
    'QTH_SIMPLE': [r'(loc|qth)',                                'my qth is {OWN_QTH} = ur qth?',           ['qth?', 'ur qth pse', 'what is ur qth?']],
    'DEFAULT':    [r'.',                                        '{OP}, hw cpy?',                           ['rst?', 'hw?', 'hw cpy?']],
}


print(apply_format(rules['OP'][1], {'OP': "Dan"}))
print(apply_format('hi there {OP}, my name is {OWN_NAME}', {'OP': "Dan"}))

input = [
    "my name is fred",
    "am hr friedrich",
    "amely hr friedrich",
    "the op hr is freddy some more text",
    "my qth   ",
    "my qth hr is berlin",
    "my qths hr is hamburg",
    "my dorf is here"
]

for msg in input:
    print ("------")
    print (f"msg: {msg}")
    print("answer:%s" % answer_it(rules, msg))

    
