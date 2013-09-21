from sniper import SniperResponse
from snipers import BaseSniper, AccessDeniedSniper

def sniper(authenticate=False):
  def sniper(func):
    def wrapper(request, *args, **kwargs):
      if authenticate and not request.user.is_authenticated():
        res = [AccessDeniedSniper()]
      else:
        res = func(request, *args, **kwargs)
      
      if isinstance(res, BaseSniper):
        response = SniperResponse(request, [res])
      else:
        response = SniperResponse(request, list(res))

      return response.to_aprop_response()

    return wrapper
  return sniper

