from app.util import util_bp

### Filter that lets one set the selected elements of a multi select list
@util_bp.app_template_filter('set_selected_for_multiselect')
def set_selected_for_multiselect(text, values):
  for v in values:
    tmpTxt = text.replace('value="{}"'.format(v.id),'selected value="{}"'.format(v.id))
    text = tmpTxt
  return text
