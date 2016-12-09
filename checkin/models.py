from django.db import models

# Create your models here.


class PatientCheckinVisitModel(models.Model):
    id = models.AutoField(primary_key = True)
    appointment_id = models.IntegerField(null = False, blank = False)
    checkin_time = models.DateTimeField(null = False, blank = False)
    in_session_time = models.DateTimeField(null = True, blank = True)


