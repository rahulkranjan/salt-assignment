from django.db import models

# Create your models here.
class Bucket(models.Model):
    """This class represents the bucketlist model."""
    name = models.CharField(max_length=350, blank=False, null= True)
    is_completed = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        db_table = 'bucket'
        ordering = ('-date_created',)