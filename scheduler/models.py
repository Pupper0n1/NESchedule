from django.db import models
from django.conf import settings

# Create your models here.
class Event(models.Model):
    EVENT_CHOICES = [
        ("RTO", "Requested Time Off"),
        ("SWP", "Swap Shift"),
        ("OTH", "Other"),
        ("BLK", "")
    ]

    STATUS_CHOICES = [
        ("P", "Pending"),
        ("A", "Approved"),
        ("D", "Denied"),
        ("O", "Other")
    ]
    person = models.ForeignKey('Person', on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=3, choices=EVENT_CHOICES)
    date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="Pending")
    boutique = models.ForeignKey('Boutique', on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    # def __str__(self):
    #     if self.time == None:
    #         return f"{self.person.f_name} is requesting {self.type} on {self.date_start} at {self.time} at {self.boutique.name}"
    #     else:
    #         return f"{self.person.f_name} is requesting {self.type} on {self.date_start} at {self.boutique.name}"

class ShiftCover(models.Model):
    covering_person = models.ForeignKey('Person', related_name='covering_person', on_delete=models.SET_NULL, null=True, blank=True)
    original_person = models.ForeignKey('Person', related_name='original_person', on_delete=models.SET_NULL, null=True, blank=True)
    boutique = models.ForeignKey('Boutique', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.covering_person.f_name} covered for {self.original_person.f_name} on {self.date}'
    
    


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
    boutique = models.ForeignKey('Boutique', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.f_name} {self.l_name} ({self.position})'
    # def __str__(self):
    #     if self.RTO_days == 0:
    #         return f"{self.f_name} {self.l_name}({self.position}) has no RTO days"
    #     else:
    #         return f"{self.f_name} {self.l_name}({self.position}): {self.RTO_days} RTO days left"

    class Meta:
        verbose_name_plural = "People"



class Boutique(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=2)
    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=6, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    MAX_RTO_CS_WEEKDAY = models.PositiveIntegerField(default=0)
    MAX_RTO_CS_WEEKEND = models.PositiveIntegerField(default=0)

    MAX_RTO_SS_WEEKDAY = models.PositiveIntegerField(default=0)
    MAX_RTO_SS_WEEKEND = models.PositiveIntegerField(default=0)

    MAX_RTO_TL_WEEKDAY = models.PositiveIntegerField(default=0)
    MAX_RTO_TL_WEEKEND = models.PositiveIntegerField(default=0)

    MAX_RTO_MG = models.PositiveIntegerField(default=0)

    MAX_RTO_TOTAL_WEEKDAY = models.PositiveIntegerField(default=0)
    MAX_RTO_TOTAL_WEEKEND = models.PositiveIntegerField(default=0)
        
    MAX_RTO_SPECIAL_EVENTS = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} in {self.city}, {self.province}"
    

class BlackoutDays(models.Model):
    boutique = models.ForeignKey('Boutique', on_delete=models.SET_NULL, null=True, blank=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Blackout Days"