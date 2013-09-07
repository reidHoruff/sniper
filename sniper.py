import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from exceptions import *
from snipers import BaseSniper

class SniperResponse(HttpResponse):
  def __init__(self, snipers=[]):
    self.snipers = snipers

  def __get_actions_list(self):
    all_snipers = []
    all_potential_snipers = self.snipers
    while all_potential_snipers:
      s = all_potential_snipers[-1]
      del all_potential_snipers[-1]
      if isinstance(s, (list, tuple)):
        all_potential_snipers += s
      elif isinstance(s, BaseSniper) or s is None:
        all_snipers.append(s)
      else:
        raise Exception("not a sniper")

    uniques = set()
    actions = []
    metas = []
    for i, s in enumerate(reversed(all_snipers)):
      if s is None or s.identity is '__bi_break':
        break
        
      if s.unique:
        if s.identity in uniques:
          raise Exception("unique sniper used more than once")
        uniques.add(s.identity)

      if s.meta:
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
    }

    return HttpResponse(
      json.dumps(response_object, indent=2),
      content_type='application/json',
    )

  def to_template_response(self):
    actions, metas = self.__get_actions_list()

    response_object = {
      '__obj_ident': '__sniper_onload',
      '__snipers': actions,
    }

    if not metas:
      raise Exception("no meta template response")

    render_info = metas[0]
    render_info.dictionary['__sniper_onload'] = json.dumps(response_object) 
    return render_to_response(
      render_info.template,
      render_info.dictionary,
      context_instance=render_info.context_instance,
    )

