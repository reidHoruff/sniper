import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from exceptions import *
from snipers import SniperObject, Break, TemplateResponse, MetaSniper, AccessDeniedSniper

class SniperResponse(object):
  def __init__(self, request, snipers=[]):
    self.snipers = snipers
    self.request = request

  def __get_actions_list(self):
    all_snipers = []
    all_potential_snipers = self.snipers
    while all_potential_snipers:
      s = all_potential_snipers[-1]
      del all_potential_snipers[-1]
      if isinstance(s, (list, tuple)):
        all_potential_snipers += s
      elif isinstance(s, SniperObject):
        all_snipers += reversed(s.AFTER_ME)
        all_snipers.append(s)
        all_snipers += reversed(s.BEFORE_ME)
      elif s is None:
        all_snipers.append(Break())
      else:
        raise TypeError("not an instance of SniperObject")

    actions = []
    metas = []
    uniques = set()
    for i, s in enumerate(reversed(all_snipers)):
      if isinstance(s, Break):
        break

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

  def to_aprop_response(self):
    actions, metas = self.__get_actions_list()

    denials = filter(lambda s: isinstance(s, AccessDeniedSniper), metas)
    if denials:
        return self.__to_access_denied_response(denials)

    template = filter(lambda s: isinstance(s, TemplateResponse), metas)
    if template:
      return self.__to_template_response(actions, template[0])

    else:
      return self.__to_ajax_response(actions)

  def __to_access_denied_response(self, denials):
    messages = map(lambda d: d.message, denials)
    response_object = {
      '__obj_ident': '__sniper_transport',
      '__snipers': [],
      '__success': False,
      '__message': messages,
    }

    return HttpResponse(
      json.dumps(response_object, indent=2),
      content_type='application/json',
    )

  def __to_ajax_response(self, actions):
    response_object = {
      '__obj_ident': '__sniper_transport',
      '__snipers': actions,
      '__success': True,
    }

    return HttpResponse(
      json.dumps(response_object, indent=2),
      content_type='application/json',
    )

  def __to_template_response(self, actions, render_info):
    response_object = {
      '__obj_ident': '__sniper_onload',
      '__snipers': actions,
      '__success': True,
    }

    print response_object
    render_info.dictionary['__sniper_onload'] = json.dumps(response_object) 
    return render_to_response(
      render_info.template,
      render_info.dictionary,
      context_instance=render_info.context_instance,
    )

