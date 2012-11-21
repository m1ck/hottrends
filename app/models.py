from django.db import models
from django.db.models import permalink
from google.appengine.ext import db



class Employee(db.Model):
  name = db.StringProperty(required=True)
  role = db.StringProperty(required=True,
                           choices=set(["executive", "manager", "producer"]))
  hire_date = db.DateProperty()
  new_hire_training_completed = db.BooleanProperty(indexed=False)
  email = db.StringProperty()