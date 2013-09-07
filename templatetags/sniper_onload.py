from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def snipe_on_load(context):
  onload = context.get('__sniper_onload', 'null')
  return """
  <script type="text/javascript">
    var __sniper_onload = %s;
  </script>
  """ % onload

