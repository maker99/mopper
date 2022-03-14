#!/usr/bin/env python3

from jinja2 import Template,Environment
templates = {
  'OP':'Hello {{ name }} my rig is {% for n in range(repeat) %} {{ rig }} {% endfor %}',
  'WX':'Hello {{ name }} my wx is {{ wx or "nice"}}'
}

vars = {
    'name' : 'mark',
    'rig' : 'FT857',
    'repeat' : 2
}

tm = Template("Hello {{ v.name }} my rig is {{v.rig}}")
msg = tm.render(v=vars)

print(msg)

def answer(rule = 'DEFAULT'): 
  print(Template(templates[rule]).render(vars, repeat=5))

answer('OP')
answer('WX')

