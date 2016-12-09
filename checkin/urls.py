from django.conf.urls import patterns, url
from checkin import views

urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^patients/$', views.PatientsView.as_view(), name= 'patients'),
    url(r'^doctors/$', views.DoctorsView.as_view(), name= 'doctor_checkin'),
    url(r'^patients/appointments$',views.AppointmentsView.as_view(), name='appointments')
]

