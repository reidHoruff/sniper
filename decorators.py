from sniper import SniperResponse
from snipers import BaseSniper

def template():
  def sniper(func):
    def wrapper(request, *args, **kwargs):
      has_auth = True
      res = func(request, *args, **kwargs)
      response = SniperResponse(request, res, has_auth)
      return response.to_template_response()

    return wrapper
  return sniper

def ajax(authenticate=False):
  def sniper(func):
    def wrapper(request, *args, **kwargs):
      if authenticate and not request.user.is_authenticated():
        has_auth = False
        res = iter([])
      else:
        has_auth = True
        res = func(request, *args, **kwargs)
      
      response = SniperResponse(request, res, has_auth)
      return response.to_ajax_response()

    return wrapper
  return sniper
