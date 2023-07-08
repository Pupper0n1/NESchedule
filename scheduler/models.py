from django.db import models

# Create your models here.
class Event(models.Model):
    EVENT_CHOICES = [
        ("RTO", "Requested Time Off"),
        ("PRF", "Preferred shift"),
        ("VAC", "Vacation"),
    ]

    STATUS_CHOICES = [
        ("P", "Pending"),
        ("A", "Approved"),
        ("D", "Denied")
    ]
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=EVENT_CHOICES)
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="Pending")

    def __str__(self):
        return f"{self.person.f_name} {self.person.l_name} is requesting {self.type} on {self.date_start} at {self.time}"



class Person(models.Model):
    POSITION_CHOICES = [
        ("CS", "Coffee Specialist"),
        ("SS", "Stock Specialist"),
        ("TL", "Team Lead"),
        ("MG", "Manager"),
        ("CB", "Coffee Bard")
    ]

    f_name = models.CharField(max_length=30)
    l_name = models.CharField(max_length=30)
    RTO_days = models.IntegerField(default=0)
    position = models.CharField(max_length=2, choices=POSITION_CHOICES)
    email = models.EmailField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.RTO_days == 0:
            return f"{self.f_name} {self.l_name}({self.position}) has no RTO days"
        else:
            return f"{self.f_name} {self.l_name}({self.position}): {self.RTO_days} RTO days left"



