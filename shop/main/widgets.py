"""
Extra HTML Widget classes
"""

import time
import datetime
import re

from django.forms.widgets import Widget, Select
from django.utils import datetime_safe
from django.utils.dates import MONTHS
from django.utils.safestring import mark_safe
from django.utils.formats import get_format
from django.conf import settings

__all__ = ('SelectDateWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')


def _parse_format(fmt):
    def pos(s):
        match = re.search('[' + s + ']', fmt)
        return match.start() + 1 if match else 0
    
    dic = {'day': pos('dj'), 'month': pos('bEFMmNn'), 'year': pos('yY')}
    return sorted(filter(None, dic.keys()), key=dic.get)


def _parse_date_fmt():
    return _parse_format(re.subn(r'\\.', '', get_format('DATE_FORMAT'))[0])


class SelectDateWidget(Widget):
    """
    A Widget that splits date input into three <select> boxes.
    
    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    """
    names = ('day', 'month', 'year',)
    none_values_dafault = '---'
    field_values = ['%s_' + n for n in names]
    fields = dict(zip(names, field_values))
    day_field, month_field, year_field = field_values
    
    def __init__(self, attrs=None, years=None, required=True,
            date_format='', none_values=None):
        # years is an optional list/tuple of years
        # to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        if not years:
            this_year = datetime.date.today().year
            years = range(this_year, this_year + 10)
        self.years = years
        self.date_format = _parse_format(date_format)
        self.none_values = none_values \
            or dict([(i, self.none_values_dafault) for i in 'dmy'])
    
    def render(self, name, value, attrs=None):

        get_names_dict = lambda l: dict(zip(self.names, l))
        
        try:
            values_list = [getattr(value, n) for n in self.names]
        except AttributeError:
            values_list = []
            if isinstance(value, basestring):
                if settings.USE_L10N:
                    try:
                        input_format = get_format('DATE_INPUT_FORMATS')[0]
                        v = datetime.datetime.strptime(value, input_format)
                        values_list = [getattr(v, n) for n in self.names]
                    except ValueError:
                        pass
                else:
                    match = RE_DATE.match(value)
                    if match:
                        values_list = (int(v) for v in match.groups())
        values = get_names_dict(values_list)
        
        choices = get_names_dict([
            [(i, i) for i in range(1, 32)],
            MONTHS.items(),
            [(i, i) for i in self.years],
        ])
        
        create_select_short = lambda n: self.create_select(
            name, self.fields[n], value, values.get(n), choices[n], n
        )
        
        htmls = get_names_dict([create_select_short(n) for n in self.names])
        
        date_format = self.date_format or _parse_date_fmt()
        output = [htmls[field] for field in date_format]
        return mark_safe(u'\n'.join(output))
    
    @classmethod
    def id_for_label(cls, id_):
        field_list = _parse_date_fmt()
        if field_list:
            first_select = field_list[0]
        else:
            first_select = 'month'
        return '%s_%s' % (id_, first_select)
    
    def value_from_datadict(self, data, files, name):
        d, m, y = (data.get(self.fields[n] % name) for n in self.names)
        if y == m == d == "0":
            return None
        if not (y and m and d):
            return data.get(name)
        if not settings.USE_L10N:
            return '%s-%s-%s' % (y, m, d)
        input_format = get_format('DATE_INPUT_FORMATS')[0]
        try:
            date_value = datetime.date(int(y), int(m), int(d))
            date_value = datetime_safe.new_date(date_value)
            return date_value.strftime(input_format)
        except ValueError:
            return '%s-%s-%s' % (y, m, d)
    
    def create_select(self, name, field, value, val, choices, date_part='d'):
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        if not (self.required and val):
            choices.insert(0, (0, self.none_values[date_part[0]]))
        local_attrs = self.build_attrs(id=field % id_)
        s = Select(choices=choices)
        select_html = s.render(field % name, val, local_attrs)
        return select_html
