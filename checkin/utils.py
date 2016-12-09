from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext

# Create your views here.
#import inspect
import requests, urllib

import datetime as dt
import time
import json


class Utils:
    def str_to_date(self, date_str):
        return dt.datetime.strptime(date_str,'%Y-%m-%dT%H:%M:%S')

    def renderedHttpResponse(self, template_name, request, context_dict):
        template = get_template(template_name)
        context = RequestContext(request, context_dict)
        return HttpResponse(template.render(context))


