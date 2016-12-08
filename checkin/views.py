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

import datetime as dt
import time
import json

from checkin.models import PatientCheckinVisitModel

def index(request):
    context_dict = {}
    context_dict['patient_checkin_url'] = 'patients/'
    context_dict['doctor_checkin_url'] = 'doctors/'
    template = get_template('checkin_index.html')
    context = RequestContext(request, context_dict)
    return HttpResponse(template.render(context))



class APIUtils:
    
    url = 'https://drchrono.com/api/'
    user = None
    def __init__(self, user):
        self.user = user
        access_token = user.social_auth.get(user = user).extra_data['access_token']
        self.headers = {'Authorization': 'Bearer {0}'.format(access_token)}
        self.headers['Content-Type'] = 'application/json'

    def build_url(self, endpoint, id):
        final_url = self.url+ endpoint
        if id is not None:
            final_url += '/' + str(id)
        return final_url

    def get(self, params, endpoint, id = None):
        url = self.build_url(endpoint, id)
        data = requests.get(url, params = params, headers = self.headers).json()
        return data

    def patch(self, params, endpoint, id):
        url = self.build_url(endpoint, id)
        print "params", params
        print "json_params", json.dumps(params)
        print "headers", self.headers
        print "url",  url
        data = requests.patch(url, params = json.dumps(params), headers = self.headers)
        return data

    def put(self, params, endpoint, id):
        url = self.build_url(endpoint, id)
        data = requests.put(url, params = json.dumps(params), headers = self.headers)
        print requests.get(url, headers = self.headers).json()
        return data

    def get_user_id(self):
        return self.user.social_auth.get(user = self.user).uid

#Needs to go into utils
def renderedHttpResponse(template_name, request, context_dict):
    template = get_template(template_name)
    context = RequestContext(request, context_dict)
    return HttpResponse(template.render(context))

class PatientsView(View):
    template_name = 'checkin_patients.html'
    def get(self, request, *args, **kwargs):
        data = request.GET.dict()
        if data.has_key('first_name') and data.has_key('last_name'):
            res = APIUtils(request.user).get(params = data, endpoint='patients', id = None)
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


class Utils:
    def str_to_date(self, date_str):
        return dt.datetime.strptime(date_str,'%Y-%m-%dT%H:%M:%S')

    


def doctor(request):
    return HttpResponse('doctor checkin')

class AppointmentsView(PatientsView):
    
    template_name = 'checkin_patients_demographics.html'
    user = None

    def get_patient(self, id):
        res = APIUtils(self.user).get(params = None, endpoint = 'patients', id = id)
        
        if res.has_key('detail') and res['detail']!='Not found.':
            return None

        return res
        
    def get_doctor_id(self, user):
        return APIUtils(user).get_user_id()

    def get_nearest_appointment(self, patient_id, doctor_id, params = {}):

        params['patient'] = patient_id
        params['doctor'] = doctor_id
        params['date'] = dt.datetime.now().strftime('%Y-%m-%d') #this is a poor implmentation
        res = APIUtils(self.user).get(params = params, endpoint = 'appointments')
        
        #If you look at theAPI, it returns the results in sorted order
        now = dt.datetime.now() - dt.timedelta(hours = 5)
        for item in res['results']:
            scheduled =  Utils().str_to_date(item['scheduled_time'])
            print scheduled, now
            if now < scheduled:
                return item                    
        return None

    def get(self, request, *args, **kwargs):
        context_dict = {}
        self.user = request.user
    
        patient = self.get_patient(request.GET.get('id'))
        nearest_appointment = self.get_nearest_appointment(patient_id = request.GET.get('id'), doctor_id = self.get_doctor_id(self.user))
        if patient and nearest_appointment:
            context_dict['appointments'] = True
            request.session['patient_id'] = request.GET.get('id')
            request.session['nearest_appointment'] = nearest_appointment['id']
    

        context_dict['form'] = PatientDemographicsForm(initial = patient)
        return renderedHttpResponse(self.template_name, request, context_dict)

    def post(self, request, *args, **kwargs):
#        print request.POST.dict()
        self.user = request.user
        #patch demogaphics
        self.put_demographics(request) #PUT & PATCH was not working was not working so mocing on to patch, modify later
        #patch appointments

        #update models
        print request.POST['id']
        self.update_checkin(patient = request.POST['id'], doctor = self.get_doctor_id(self.user))
        return HttpResponse('Manu')

    def update_checkin(self, patient, doctor, *args, **kwargs):
        patient_id = patient
        doctor_id = doctor
        print "yo"
        checkin_time = dt.datetime.now()
        Patient = PatientCheckinVisitModel(patient_id = patient_id, doctor_id = doctor_id, checkin_time = checkin_time)
        Patient.save()

    def put_demographics(self, request, *args, **kwargs):
        params = request.POST.dict()
        del params['id'] 
        del params['csrfmiddlewaretoken']
        params['zip_code'] = int(params['zip_code'])
        patient  = self.get_patient(request.POST['id'])
        data = APIUtils(request.user).patch(params , endpoint = 'patients', id=request.POST['id'])
        print data
        
