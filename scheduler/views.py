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
                "title": i.person.f_name + " " + i.date_time.strftime("%H:%M %p"),
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
                "color": "orange",
                "id"    : i.id
            })
    print(events_json)


    context = {"people" : Person.objects.all(), "events": events_json}

    return render(request, "scheduler/index.html", context)
    # return HttpResponse("Hello, world. You're at the scheduler index.")


def create_event(request):
    if request.method == 'POST':
        # Extract the event data from the form
        person = Person.objects.get(f_name = request.POST.get('person'))
        type = request.POST.get('options-outlined')

        date = request.POST.get('date')
        if type == "PRF":
            time = request.POST.get('time')
            date = date + " " + time

        event = Event.objects.create(person=person, type=type, date_time=date)
        # print(event)
        # event.save()

        # Optionally, redirect the user to a success page
        # return render(request, 'scheduler/index.html')
        return redirect(reverse('scheduler:index'))


def delete_event(request):
    if request.method == 'POST':
        event = request.POST.get('event_id')
        Event.objects.get(id=event).delete()
        # print("HI")
        # Extract the event data from the form
        # event = Event.objects.get(id=request.POST.get('event_id'))
        # event.delete()

        # Optionally, redirect the user to a success page
        # return render(request, 'scheduler/index.html')
        return redirect(reverse('scheduler:index'))
        # return HttpResponse("YUP")