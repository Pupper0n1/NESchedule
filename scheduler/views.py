from django.shortcuts import render
from django.http import HttpResponse
from .models import Event, Person
from django.shortcuts import redirect
from django.urls import reverse
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest
import re
from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
def index_view(request):
    # return render(request, 'scheduler/index.html')
    events = Event.objects.all()

    events_json = []

    for i in events:
        if i.type == "PRF":
            events_json.append({
                "title": i.person.f_name + " " + i.time.strftime("%I:%M %p"),
                "type": i.type,
                "start": i.date_start.strftime("%Y-%m-%d"),
                "color": "green",
                "id": i.id,
                "type": i.type
            })
        else:
            events_json.append({
                "title": i.person.f_name + " RTO",
                "type": i.type,
                "start": i.date_start.strftime("%Y-%m-%d"),
                "end": i.date_end.strftime("%Y-%m-%d"),
                "color": "orange",
                "id": i.id,
                "type": i.type
            })
        if i.status =='P':
            events_json[-1]["color"] = "gray"
        elif i.status =='R':
            events_json[-1]["color"] = "red"
    # print(events_json)


    context = {"people" : Person.objects.all(), "events": events_json}

    return render(request, "scheduler/index.html", context)
    # return HttpResponse("Hello, world. You're at the scheduler index.")





TIME_FORMAT_REGEX = r'^\d{2}:\d{2}$'  # Regular expression for HH:MM format

def create_event(request):
    if request.method != 'POST':
        return redirect(reverse('scheduler:index'))

    person_name = request.POST.get('person')
    event_type = request.POST.get('options-outlined')
    date_start = request.POST.get('date')

    try:
        person = Person.objects.get(f_name=person_name)
    except Person.DoesNotExist:
        return redirect(reverse('scheduler:index'))

    if event_type == "PRF":
        time = request.POST.get('time')
        if not re.match(TIME_FORMAT_REGEX, time):
            return HttpResponseBadRequest("Invalid time format")
    else:
        rto_events_count = Event.objects.filter(type="RTO", date_start=date_start).count()
        if person.RTO_days <= 0:
            return HttpResponseBadRequest("RTO days are already 0")
        elif rto_events_count >= 2:
            return HttpResponseBadRequest("Too many RTO requests for this day")

        time = None

    obj = Event.objects.create(person=person, type=event_type, date_start=date_start, date_end=date_start, time=time, status="P")
    print(obj.pk)
    
    # Email stuff
    message = (f"""An {event_type} request by {person_name} for {date_start} has been submitted and is pending approval.\n\n
               click here to see the request: http://pupper1n0.pythonanywhere.com/scheduler/ \n\n
               Otherwise, click here to quick approve http://pupper1n0.pythonanywhere.com/quick-approve/{obj.pk}\n
               TEMP: http://127.0.0.1:8000/quick-approve/{obj.pk}\n\n
               Thank you,\nScheduler""")
    email = 'elbouni.wassem@gmail.com'
    subject = 'Event Needs Approval'
    print("HI")
    send_mail(
        subject,
        message,
        'settings.EMAIL_HOST_USER',
        [email],
        fail_silently=False,
    )

    return redirect(reverse('scheduler:index'))


def quick_approve(request, pk):
    event = Event.objects.get(id=pk)
    event.status = "A"
    event.save()
    return redirect(reverse('scheduler:index'))

def delete_event(request):
    if request.method == 'POST':
        event = request.POST.get('event_id')
        Event.objects.get(id=event).delete()
        return redirect(reverse('scheduler:index'))


def set_event_status(request):
    if request.method == 'POST':
        # print("HI")
        event_id = request.POST.get('event_id')
        status = request.POST.get('status')
        obj = Event.objects.get(id=event_id)
        # Perform actions based on the status value
        if status == 'A' and obj.status != "A":
            if obj.type == "RTO":
                person = Person.objects.get(id=obj.person.id)
                if person.RTO_days <= 0:
                    return HttpResponseBadRequest("RTO days are already 0")
                person.RTO_days = person.RTO_days - 1
                person.save()
            obj.status = "A"
            obj.save()
        elif status == 'R':
            obj.status = "R"
            obj.save()
        elif status == 'D':
            obj.delete()
        return redirect(reverse('scheduler:index'))



def redirect_index(request):
    return redirect(reverse('scheduler:index'))


def login(request):
    return render(request, 'scheduler/login.html')