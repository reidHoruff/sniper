from sniper import SniperResponse
from snipers import BaseSniper

def ajax(func):
  def wrapper(*args, **kwargs):
    res = func(*args, **kwargs)
    
    if isinstance(res, BaseSniper):
      response = SniperResponse([res])
    else:
      response = SniperResponse(list(res))

    return response.to_ajax_response()

  return wrapper

def template(func):
  def wrapper(*args, **kwargs):
    res = func(*args, **kwargs)
    
    if isinstance(res, BaseSniper):
      response = SniperResponse([res])
    else:
      response = SniperResponse(list(res))

    return response.to_template_response()

  return wrapper


