#!/usr/bin/env python3

from unittest import result
import  jinja2 
import hashlib

def j2_hash_filter(value, hash_type="sha1"):
    """
    Example filter providing custom Jinja2 filter - hash

    Hash type defaults to 'sha1' if one is not specified

    :param value: value to be hashed
    :param hash_type: valid hash type
    :return: computed hash as a hexadecimal string
    """
    hash_func = getattr(hashlib, hash_type, None)

    if hash_func:
        computed_hash = hash_func(value.encode("utf-8")).hexdigest()
    else:
        raise AttributeError(
            "No hashing function named {hname}".format(hname=hash_type)
        )

    return computed_hash
  
def j2_repeat_filter(value, repeat=1):
    """
    Example filter providing custom Jinja2 filter - repeat

    repeat value defaults to 1 if one is not specified

    :param value: value to be repeated
    :param repeat: how often to repeat
    :return: string
    """

    # if hash_func:
    #     computed_hash = hash_func(value.encode("utf-8")).hexdigest()
    # else:
    #     raise AttributeError(
    #         "No hashing function named {hname}".format(hname=hash_type)
    #     )

    result = [str(value)] * repeat
    
    return ' '.join(result)
  
env = jinja2.Environment()
env.filters["hash"] = j2_hash_filter
env.filters["repeat"] = j2_repeat_filter
env.filters["R"] = j2_repeat_filter

tmpl_string = """MD5 hash of '$3cr3tP44$$': {{ '$3cr3tP44$$' | hash('md5') }}"""
tmpl = env.from_string(tmpl_string)
print(tmpl.render())  

vars = {'RIG': 'FT857','ANT': 'DIPOLE','OM': '','RPT':4}

tmpl_string = """my rig is  {{ RIG| R(RPT) }}   {{ 3 | R(RPT) }} """
tmpl = env.from_string(tmpl_string)
print(tmpl.render(vars,RPT=2))  

macro_string = """
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
        
    {%- macro ANS(_MYVAR,_VAL,_REPEAT) -%}
        {{ RND(['the ', 'my ', ' ']) }}{{ _MYVAR }} {{ RND(['hr is ', 'is ','hr ', '']) }}{{ REP(_VAL or "nice",_REPEAT or RPT)}}
    {%- endmacro -%}
    
    """
    
def answer(tmpl_string:str):
    # tmpl_string = 'my rig is -{{ REP(RIG) }}- -{{ REP(ANT,4)}}- --'
    tmpl = env.from_string(macro_string+tmpl_string)
    print(tmpl.render(vars,RPT=2))  

answer('my rig is {{ REP(RIG) }} = {{ REP(ANT,4)}}')
answer('{{ UR() }} = {{ ANS("rig",RIG) }} = {{ ANS("ant",ANT,5) }} = {{ ANS("qth",QTH) }}')
answer('{{ GREETING("ge") }} = {{ UR() }}')

# templates = {
#   'OP':'Hello {{ name }} my rig is {% for n in range(repeat) %} {{ rig }} {% endfor %}',
#   'WX':'Hello {{ name }} my wx is {{ wx or "nice"}}'
# }

# vars = {
#     'name' : 'mark',
#     'rig' : 'FT857',
#     'repeat' : 2
# }

# tm = Template("Hello {{ v.name }} my rig is {{v.rig}}")
# msg = tm.render(v=vars)

# print(msg)

# def answer(rule = 'DEFAULT'): 
#   print(Template(templates[rule]).render(vars, repeat=5))

# answer('OP')
# answer('WX')

