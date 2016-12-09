from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.views.generic import View, TemplateView

from django.template.loader import get_template
from django.template import RequestContext


from checkin.utils import Utils
from checkin.api_utils import APIUtils
from checkin.forms import PatientCheckinForm
from checkin.forms import PatientDemographicsForm

# Create your views here.

#import inspect
import datetime as dt
import time

from checkin.models import PatientCheckinVisitModel

def index(request):
    context_dict = {}
    context_dict['patient_checkin_url'] = 'patients/'
    context_dict['doctor_checkin_url'] = 'doctors/'
    template = get_template('checkin_index.html')
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
                context_dict['error'] = data['error']
            context_dict = {}
            context_dict['form'] = PatientCheckinForm
            return Utils().renderedHttpResponse(self.template_name, request, context_dict)


   


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
        params['date'] = (dt.datetime.now() - dt.timedelta(hours=5))#this is a poor implmentation
        res = APIUtils(self.user).get(params = params, endpoint = 'appointments')
        print "------", res['results']
        res['results'] = [item for item in res['results'] if not item['status']]
        print [item for item in res['results'] if item['status']]
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
        return Utils().renderedHttpResponse(self.template_name, request, context_dict)

    def post(self, request, *args, **kwargs):
        self.user = request.user
        self.patch_demographics(request) #PUT & PATCH was not working was not working so mocing on to patch, modify later
        #patch appointments
        #update models
        self.patch_appointments(request)
        self.update_checkin(request.session['nearest_appointment'])
        return HttpResponseRedirect('/checkin/patients/')

    def update_checkin(self, appointment, *args, **kwargs):
        checkin_time = dt.datetime.now()
        Patient = PatientCheckinVisitModel(appointment_id = appointment, checkin_time = checkin_time)
        Patient.save()

    def patch_appointments(self, request, *args, **kwargs):
        params = {}
        params['status'] = 'Arrived'
        appointment = request.session['nearest_appointment']
        data = APIUtils(request.user).patch(params, endpoint = 'appointments', id =  appointment)
        

    def patch_demographics(self, request, *args, **kwargs):
        params = request.POST.dict()
        patient  = self.get_patient(request.POST['id'])
        data = APIUtils(request.user).patch(params , endpoint = 'patients', id=request.POST['id'])



class DoctorsView(View):

    template_name = 'checkin_doctors.html'
    user = None
    def get(self, request, *args, **kwargs):
        context_dict = {}
        
        #calculate overall average over here, add to the context dict
                
        context_dict['checkin']  = PatientCheckinVisitModel.objects.filter(in_session_time__isnull = True)
        already_checked_in  = PatientCheckinVisitModel.objects.filter(in_session_time__isnull = False)
        timediff_checkin_session = [((item.in_session_time - item.checkin_time).seconds)//60 for item in already_checked_in]
        average = sum(timediff_checkin_session) / len(timediff_checkin_session)

        context_dict['average'] = average

        return Utils().renderedHttpResponse(self.template_name, request, context_dict)

    def post(self, request, *args, **kwargs):
        self.user = request.user
        checkin_id = request.POST['checkin']       
        checkin_model = PatientCheckinVisitModel.objects.get(id = checkin_id)
        checkin_model.in_session_time = dt.datetime.now()
        checkin_model.save()

        return HttpResponseRedirect('/checkin/doctors/')


    def calculate_overall_average(self):
        objects = PatientCheckinVisitModel.objects.exclude(checkin_time = False, in_session_time = False)
