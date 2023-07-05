from django.shortcuts import render
from django.http import HttpResponse
from .models import Event, Person
from django.shortcuts import redirect
from django.urls import reverse

# Create your views here.
def index_view(request):
    # return render(request, 'scheduler/index.html')
    events = Event.objects.all()

    events_json = []

    for i in events:
        if i.type == "PRF":
            events_json.append({
                "title": i.person.f_name + " " + i.date_time.strftime("%I:%M %p"),
                "type": i.type,
                "start": i.date_time.strftime("%Y-%m-%d"),
                "color": "green",
                "id": i.id
            })
        else:
            events_json.append({
                "title": i.person.f_name + " RTO",
                "type": i.type,
                "start": i.date_time.strftime("%Y-%m-%d"),
                "end": i.date_end.strftime("%Y-%m-%d"),
                "color": "orange",
                "id"    : i.id
            })
    # print(events_json)


    context = {"people" : Person.objects.all(), "events": events_json}

    return render(request, "scheduler/index.html", context)
    # return HttpResponse("Hello, world. You're at the scheduler index.")


def create_event(request):
    if request.method == 'POST':
        # Extract the event data from the form
        person = None
        try:
            person = Person.objects.get(f_name = request.POST.get('person'))
        except Person.DoesNotExist:
            return redirect(reverse('scheduler:index'))
        type = request.POST.get('options-outlined')

        date = request.POST.get('date')
        
        date_end = None
        if type == "PRF":
            try:
                time = request.POST.get('time')
                date = date + " " + time
            except:
                return redirect(reverse('scheduler:index'))
        else:
            date_end = request.POST.get('date_end')

        event = Event.objects.create(person=person, type=type, date_time=date, date_end=date_end, status="P")
        print(event)
        event.save()

        # Optionally, redirect the user to a success page
        # return render(request, 'scheduler/index.html')
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