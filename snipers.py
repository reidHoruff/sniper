from django.template.loader import render_to_string

class BaseSniper:
  identity = None
  unique = False
  template_only = False
  meta = False

  def get_args(self):
    if not self.identity:
      raise Exception("identity not set")

    if not isinstance(self.identity, str):
      raise Exception("identity must be a string")

    if not hasattr(self, 'kwargs'):
      raise Exception("must have kwargs attribute")

    if not isinstance(self.kwargs, dict):
      raise Exception("kwargs property must by a dictionary")

    return {
      '__sniper_ident': self.identity,
      '__sniper_kwargs': self.kwargs,
      '__index': self.index,
    }

class MetaSniper(BaseSniper):
  meta = True
  
class JSLog(BaseSniper):
  identity = '__bi_js_log'
  def __init__(self, *args):
    self.kwargs = {
      'args': map(str, args),
    }

class InsertText(BaseSniper):
  identity = '__bi_insert_text'
  def __init__(self, ident, text):
    self.kwargs = {
      'text': text,
      'dom_ident': ident,
    }

class AppendText(BaseSniper):
  identity = '__bi_append_text'
  def __init__(self, ident, text):
    self.kwargs = {
      'text': text,
      'dom_ident': ident,
    }

class InsertTemplate(BaseSniper):
  identity = '__bi_insert_text'
  def __init__(self, ident, template, args={}, context_instance=None):
    self.kwargs = {
      'text': render_to_string(template, args, context_instance),
      'dom_ident': ident,
    }

class AppendTemplate(BaseSniper):
  identity = '__bi_append_text'
  def __init__(self, ident, template, args={}, context_instance=None):
    self.kwargs = {
      'text': render_to_string(template, args, context_instance),
      'dom_ident': ident,
    }

class RefreshBrowser(BaseSniper):
  identity = '__bi_refresh'
  def __init__(self):
    self.kwargs = {}

class DeleteFromDOM(BaseSniper):
  identity = '__bi_dom_delete'
  def __init__(self, ident):
    self.kwargs = {
      'dom_ident': ident,
    }

class RedirectBrowser(BaseSniper):
  identity = '__bi_redirect'
  def __init__(self, href):
    self.kwargs = {
      'href': href,
    }

class AlertDialog(BaseSniper):
  identity = '__bi_alert'
  def __init__(self, text):
    self.kwargs = {
      'text': text
    }

class SetCSS(BaseSniper):
  identity = '__bi_set_css'
  def __init__(self, selector, values):
    self.kwargs = {
      'selector': selector,
      'values': values,
    }

class JSCall(BaseSniper):
  identity = '__bi_js_call'
  def __init__(self, name, *args):
    self.kwargs = {
      'name': name,
      'args': args,
    }

class SniperTemplateResponse(MetaSniper):
  identity = '__bi_template_response'
  def __init__(self, template, dictionary={}, context_instance=None, content_type=None):
    self.template = template
    self.dictionary = dictionary
    self.context_instance = context_instance
    self.content_type = content_type
    self.kwargs = {}

class Break(MetaSniper):
  identity = '__bi_break'
