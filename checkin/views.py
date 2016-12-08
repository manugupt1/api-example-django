from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.views.generic import View, TemplateView

from django.template.loader import get_template
from django.template import RequestContext



from checkin.forms import PatientCheckinForm
from checkin.forms import PatientDemographicsForm
#import social_auth_drchrono as social_auth

# Create your views here.

#import inspect
import requests, urllib



def index(request):
    context_dict = {}
    context_dict['patient_checkin_url'] = 'patients/'
    context_dict['doctor_checkin_url'] = 'doctors/'
    template = get_template('checkin_index.html')
    context = RequestContext(request, context_dict)
    return HttpResponse(template.render(context))



class APIUrlBuilder:
    
    url = 'https://drchrono.com/api/'
    def __init__(self, user):
        access_token = user.social_auth.get(user = user).extra_data['access_token']
        self.headers = {'Authorization': 'Bearer {0}'.format(access_token)}
    
    def build_url(self, endpoint, id):
        final_url = self.url+ endpoint
        if id is not None:
            final_url += '/' + str(id)
        return final_url

    def get(self, params, endpoint, id = None):
        url = self.build_url(endpoint, id)
        data = requests.get(url, params = params, headers = self.headers).json()
        return data


def renderedHttpResponse(template_name, request, context_dict):
    template = get_template(template_name)
    context = RequestContext(request, context_dict)
    return HttpResponse(template.render(context))

class PatientsView(View):
    template_name = 'checkin_patients.html'
    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        if data.has_key('first_name') and data.has_key('last_name'):
            api = APIUrlBuilder(request.user)
            res = api.get(params = data, endpoint='patients', id = None)
            if len(res['results'])==1:
                return HttpResponseRedirect('/checkin/patients/appointments?id='+str(res['results'][0]['id']))
            return HttpResponseRedirect('/checkin/patients?error=1')
        else:
            if data.has_key('error') and data['error']==1:
                # Integrate it with templates
                context_dict['error'] = data['error']
            context_dict = {}
            context_dict['form'] = PatientCheckinForm
            return renderedHttpResponse(self.template_name, request, context_dict)



def doctor(request):
    return HttpResponse('doctor checkin')


class AppointmentsView(PatientsView):
    
    template_name = 'checkin_patients_demographics.html'

    def get(self, request, *args, **kwargs):
        context_dict = {}
        api = APIUrlBuilder(request.user)
        res = api.get(params = None, endpoint = 'patients', id = request.GET.get('id'))
        
        context_dict['form'] = PatientDemographicsForm(initial = res)
        return renderedHttpResponse(self.template_name, request, context_dict)

    def post(self, request, *args, **kwargs):
        print request.POST.dict()
        return HttpResponse('Manu')
