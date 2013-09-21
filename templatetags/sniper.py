from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def sniper_onload(context):
  onload = context.get('__sniper_onload', 'null')
  return """
  <script type="text/javascript">
    var __sniper_onload = %s;
  </script>
  """ % onload
