from django.template.loader import render_to_string
from django.template import RequestContext
import cgi

class SniperObject:
  UNIQUE = False
  BEFORE_ME = []
  AFTER_ME = []

  def process(self, request):
    pass

  def __hash__(self):
    return hash(self.__class__.__name__)

class BaseSniper(SniperObject):
  IDENTITY = None
  template_only = False
  meta = False

  def __init__(self):
    self.kwargs = {}
    self.index = 0
    self.identity = None

  def set_arg(self, key, value):
    if not isinstance(key, str):
      raise TypeError("Sniper key must be string")

    self.kwargs[key] = cgi.escape(value).encode('ascii', 'xmlcharrefreplace')

  def __setitem__(self, key, value):
    self.set_arg(key, value)

  def __getitem__(self, key):
    return self.kwargs.get(key, None)

  def __delitem__(self, key):
    del self.kwargs[key]

  def get_args(self):
    if not self.IDENTITY:
      raise Exception("identity not set: %s", self)

    if not isinstance(self.IDENTITY, str):
      raise Exception("identity must be a string")

    if not hasattr(self, 'kwargs'):
      raise Exception("must have kwargs attribute")

    if not isinstance(self.kwargs, dict):
      raise Exception("kwargs property must by a dictionary")

    return {
      '__sniper_ident': self.IDENTITY,
      '__sniper_kwargs': self.kwargs,
      '__index': self.index,
    }

class JSLog(BaseSniper):
  IDENTITY = '__bi_js_log'
  def __init__(self, *args):
    self.kwargs = {
      'args': map(str, args),
    }

class InsertText(BaseSniper):
  IDENTITY = '__bi_insert_text'
  def __init__(self, ident, text):
    self.kwargs = {
      'text': text,
      'dom_ident': ident,
    }

class AppendText(BaseSniper):
  IDENTITY = '__bi_append_text'
  def __init__(self, ident, text):
    self.kwargs = {
      'text': text,
      'dom_ident': ident,
    }

class BaseTemplateSniper(BaseSniper):
  def __init__(self, ident, template, args={}, context_instance=None, request_context=False):
    self.ident = ident
    self.template = template
    self.args = args
    self.context_instance = context_instance
    self.request_context = request_context
    BaseSniper.__init__(self)

  def process(self, request):
    if self.request_context:
      context_instance = RequestContext(request)
    else:
      context_instance = self.context_instance

    self['text'] = render_to_string(self.template, self.args, context_instance)
    self['dom_ident'] = self.ident

class InsertTemplate(BaseTemplateSniper):
  IDENTITY = '__bi_insert_text'

class AppendTemplate(BaseTemplateSniper):
  IDENTITY = '__bi_append_text'

class RefreshBrowser(BaseSniper):
  IDENTITY = '__bi_refresh'
  def __init__(self):
    self.kwargs = {}

class DeleteFromDOM(BaseSniper):
  IDENTITY = '__bi_dom_delete'
  def __init__(self, ident):
    self.kwargs = {
      'dom_ident': ident,
    }

class RedirectBrowser(BaseSniper):
  IDENTITY = '__bi_redirect'
  def __init__(self, href):
    self.kwargs = {
      'href': href,
    }

class AlertDialog(BaseSniper):
  IDENTITY = '__bi_alert'
  def __init__(self, text):
    self.kwargs = {
      'text': text
    }

class SetCSS(BaseSniper):
  IDENTITY = '__bi_set_css'
  def __init__(self, selector, values):
    self.kwargs = {
      'selector': selector,
      'values': values,
    }

class PushState(BaseSniper):
  IDENTITY = '__bi_push_state'
  def __init__(self, url):
    self.kwargs = {
      'url': url,
    }

class JSCall(BaseSniper):
  IDENTITY = '__bi_js_call'
  def __init__(self, name, *args):
    self.kwargs = {
      'name': name,
      'args': args,
    }

class MetaSniper(SniperObject):
  pass
  
class Break(MetaSniper):
  pass

class PageResponse(MetaSniper):
  UNIQUE=True

class TemplateResponse(PageResponse):
  def __init__(self, template, dictionary={}, context_instance=None, request_context=False, content_type=None):
    self.template = template
    self.dictionary = dictionary
    self.context_instance = context_instance
    self.content_type = content_type
    self.request_context = request_context

  def process(self, request):
    if self.request_context:
      self.context_instance = RequestContext(request)

class AccessDeniedSniper(MetaSniper):
  def __init__(self, message='access denied'):
    self.message = message
