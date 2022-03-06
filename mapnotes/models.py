from datetime import timezone
import datetime
from django.db import models

# Create your models here.
# Examples Subclasses Model
# Format --> field = value type

# class Question(models.Model): 
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')

# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)

# The below table is equivalent to executing the following:
# CREATE TABLE mapnotes_User (
#     "id" serial NOT NULL PRIMARY KEY,
#     "fname" varchar(50) NOT NULL,
#     "lname" varchar(50) NOT NULL
# );
class User(models.Model): # id field is added automatically
    display_name = models.CharField(max_length=80)
    email = models.TextField(max_length=320)
    fname = models.CharField(max_length=50) # first name
    lname = models.CharField(max_length=50) # last name

    def __str__(self): # toString()
        return ('User: {0}'.format(self.display_name))

class Note(models.Model):
    # if user deleted, also delete their notes
    creator = models.ForeignKey(User, on_delete=models.CASCADE) 
    body = models.TextField(max_length=1000) # > 255 character text
    date = models.DateTimeField('date published')

    # Location of Note
    # Usage: import geocoder   g = geocoder.ip('me')   g.latlng
    lat = models.DecimalField(max_digits=30, decimal_places=25)
    lon = models.DecimalField(max_digits=30, decimal_places=25)

    upvotes = models.IntegerField(default=0) # ? optional

    def __str__(self): # toString()
        return ('\'{0}\', note by {1}'.format(self.body, self.creator))
        
    # Returns true if note was published less than or equal to a day from now
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)




