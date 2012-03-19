from django.conf import settings  
from django.forms.widgets import Textarea  
from django.db.models import SubfieldBase, TextField  
from django.utils import simplejson  
  
  
class JSONField(TextField):  
    __metaclass__ = SubfieldBase  
  
    def contribute_to_class(self, cls, name):  
        super(JSONField, self).contribute_to_class(cls, name)  
  
        def get_json(model):  
            return self.get_db_prep_value(getattr(model, self.attname))  
        setattr(cls, 'get_%s_json' % self.name, get_json)  
  
        def set_json(model, json):  
            setattr(model, self.attname, self.to_python(json))  
        setattr(cls, 'set_%s_json' % self.name, set_json)  
  
    def formfield(self, **kwargs):  
        kwargs['widget'] = JSONWidget(attrs={'class': 'vLargeTextField'})  
        return super(JSONField, self).formfield(**kwargs)  
  
    def get_db_prep_value(self, value):  
        return simplejson.dumps(value)  
  
    def to_python(self, value):  
        if not isinstance(value, basestring):  
            return value  
  
        try:  
            return simplejson.loads(value, encoding=settings.DEFAULT_CHARSET)  
        except ValueError, e:  
            # If string could not parse as JSON it's means that it's Python  
            # string saved to JSONField.  
            return value  
  
class JSONWidget(Textarea):  
    """ 
    Prettify dumps of all non-string JSON data. 
    """  
    def render(self, name, value, attrs=None):  
        if not isinstance(value, basestring) and value is not None:  
            value = simplejson.dumps(value, indent=4, sort_keys=True)  
        return super(JSONWidget, self).render(name, value, attrs)  