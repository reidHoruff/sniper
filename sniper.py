import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from exceptions import *
from snipers import SniperObject, Break, TemplateResponse, MetaSniper 
from django.conf import settings

class stack:
  def __init__(self):
    self.s = list()

  def push(self, obj):
    self.s.append(obj)

  def pop(self):
    o = self.s[-1]
    del self.s[-1]
    return o

  def push_all(self, objs):
    self.s += objs

  def push_all_r(self, objs):
    self.s += reversed(objs)

  def as_list(self):
    return self.s

  def empty(self):
    return not bool(self.s)

class SniperResponse(object):
  def __init__(self, request, snipers=iter([]), has_auth=True):
    self.snipers = snipers
    self.request = request
    self.has_auth = has_auth

  def __get_actions_list(self):
    working_stack = stack()
    output_stack = stack()

    while True:
      if working_stack.empty():
        try:
          working_stack.push(self.snipers.next())
        except StopIteration:
          break
      
      s = working_stack.pop()

      if isinstance(s, (list, tuple)):
        working_stack.push_all_r(s)
      elif isinstance(s, SniperObject):
        output_stack.push_all(s.BEFORE_ME)
        output_stack.push(s)
        output_stack.push_all(s.AFTER_ME)
      elif s is None:
        break
      else:
        raise TypeError("not an instance of SniperObject")

    actions = []
    metas = []
    uniques = set()
    for i, s in enumerate(output_stack.as_list()):
      if s.UNIQUE:
        if s in uniques:
          raise Exception("must be unique")
        uniques.add(s)

      s.process(self.request)

      if isinstance(s, MetaSniper):
        metas.append(s)
      else:
        s.index = i
        actions.append(s.get_args())

    return actions, metas

  def to_ajax_response(self):
    actions, metas = self.__get_actions_list()

    response_object = {
      '__obj_ident': '__sniper_transport',
      '__snipers': actions,
      '__success': self.has_auth,
    }

    if not self.has_auth:
      response_object['__message'] = 'Access Denied'

    return HttpResponse(
      json.dumps(response_object, indent=2),
      content_type='application/json',
    )

  def to_template_response(self):
    actions, metas = self.__get_actions_list()
    
    templates = filter(lambda s: isinstance(s, TemplateResponse), metas)

    if len(templates) != 1:
      raise Exception('Sniper Template Response must have exactly one Instance of TemplateResponse')

    render_info = templates[0]

    response_object = {
      '__obj_ident': '__sniper_onload',
      '__snipers': actions,
      '__success': True,
    }

    render_info.dictionary['__sniper_onload'] = json.dumps(response_object) 

    return render_to_response(
      render_info.template,
      render_info.dictionary,
      context_instance=render_info.context_instance,
    )

