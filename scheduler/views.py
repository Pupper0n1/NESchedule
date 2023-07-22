from django.shortcuts import render
from django.http import HttpResponse
from .models import Event, Person
from django.shortcuts import redirect
from django.urls import reverse
from datetime import datetime
from django.http import HttpResponseBadRequest
import re
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
import random
import string
from datetime import date

# Maximum number of rtos per day by position and date
MG_RTO_MAX = 1
TL_RTO_MAX = 1
CS_RTO_MAX_MON_THR = 2
CS_RTO_MAX_FRI_SUN = 1
SS_RTO_MAX = 1


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# Create your views here.
def index_view(request):
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponseBadRequest("Invalid username or password")

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
            })
        elif i.type == "RTO":
            events_json.append({
                "title": i.person.f_name + " RTO",
                "type": i.type,
                "start": i.date_start.strftime("%Y-%m-%d"),
                "end": i.date_end.strftime("%Y-%m-%d"),
                "color": "orange",
                "id": i.id,
            })
        else:
            events_json.append({
            "title": i.person.f_name + " Vacation",
            "type": i.type,
            "start": i.date_start.strftime("%Y-%m-%d"),
            "end": i.date_end.strftime("%Y-%m-%d"),
            "color": "blue",
            "id": i.id,
            })
        if i.status =='P':
            events_json[-1]["color"] = "gray"
        elif i.status =='R':
            events_json[-1]["color"] = "red"
    # print(events_json)


    context = {"people" : Person.objects.all().order_by('f_name'), "events": events_json}

    return render(request, "scheduler/index.html", context)
    # return HttpResponse("Hello, world. You're at the scheduler index.")





TIME_FORMAT_REGEX = r'^\d{2}:\d{2}$'  # Regular expression for HH:MM format

def create_event(request):
    if request.method != 'POST':
        return redirect(reverse('scheduler:index'))

    person_name = request.POST.get('person')
    event_type = request.POST.get('options-outlined')
    date_start = request.POST.get('date')
    time = None


    try: # Check if the person exists
        person = Person.objects.get(f_name=person_name)
    except Person.DoesNotExist:
        return redirect(reverse('scheduler:index'))

    if event_type == "PRF": # If the event is a PRF, get the time
        time = request.POST.get('time')
        if not re.match(TIME_FORMAT_REGEX, time):
            return HttpResponseBadRequest("Invalid time format")
        time = datetime.strptime(time, "%H:%M").time()

        
    date = datetime.strptime(date_start, "%Y-%m-%d")
    # Check if the person already has an event on that day
    events = Event.objects.filter(date_start=date_start)

    if events.filter(person__f_name=person_name).exists(): # If the person already has an event on that day
        return HttpResponseBadRequest("Person already has an event on that day")
    
    
    # Get the number of RTOs for that day and position
    total_rto_events = events.filter(type="RTO").count()
    tl_rto_events = events.filter(type="RTO", person__position="TL").count()
    cs_rto_events = events.filter(type="RTO", person__position="CS").count()
    ss_rto_events = events.filter(type="RTO", person__position="SS").count()
    mg_rto_events = events.filter(type="RTO", person__position="MG").count()

    # Check if the person has reached the maximum number of RTOs for that day and position
    if event_type == "RTO":
        if person.RTO_days <= 0:
            return HttpResponseBadRequest("RTO days are already 0")
        if total_rto_events > 3:
            return HttpResponseBadRequest("Total RTO max reached")
        if person.position == "TL" and tl_rto_events >= TL_RTO_MAX:
            return HttpResponseBadRequest("TL RTO max reached")
        elif person.position == "CS" and cs_rto_events >= CS_RTO_MAX_MON_THR and date.weekday() < 4:
            return HttpResponseBadRequest("CS Monday to Thursday RTO max reached")
        elif person.position == "CS" and cs_rto_events >= CS_RTO_MAX_FRI_SUN and date.weekday() > 3:
            return HttpResponseBadRequest("CS Friday to Sunday RTO max reached")
        elif person.position == "SS" and ss_rto_events >= SS_RTO_MAX:
            return HttpResponseBadRequest("SS RTO max reached")
        elif person.position == "MG" and mg_rto_events >= MG_RTO_MAX:
            return HttpResponseBadRequest("MG RTO max reached")
        


    obj = Event.objects.create(person=person, type=event_type, date_start=date_start, date_end=date_start, time=time, status="P")
    context = {
        "person": person_name,
        "event_type": event_type,
        "date": date_start,
        "time": time,
        "event_id": obj.pk,
    }

    # # Email stuff DO NOT ENABLE UNTIL PERMISSION IS GRANTED BY STAFF MEMBERS
    # subject = 'Event Needs Approval'
    # html_message = render_to_string('../templates/scheduler/request_email.html', context)
    # plain_message = strip_tags(html_message)
    # from_email = 'settings.EMAIL_HOST_USER'
    # # message =  f"""<strong>{event_type}</strong> request by <strong>{person_name}</strong> for <strong>{date_start}</strong> has been submitted and is pending approval.\n\n
    # # click here to see the request: http://pupper1n0.pythonanywhere.com/scheduler/ \n\n
    # # Otherwise, click here to quick approve http://pupper1n0.pythonanywhere.com/quick-approve/{obj.pk}\n
    # # TEMP: http://127.0.0.1:8000/quick-approve/{obj.pk}\n\n
    # # Thank you,\nScheduler"""
    # to_email = ['elbouni.wassem@gmail.com']     # Will be changed to the email of the person in charge of approving events
    # send_mail(
    #     subject,
    #     plain_message,
    #     from_email,
    #     to_email,
    #     html_message=html_message,
    #     fail_silently=False,
    # )

    # subject = 'Event submitted!'
    # html_message = render_to_string('../templates/scheduler/request_email.html', context)
    # plain_message = strip_tags(html_message)
    # from_email = 'settings.EMAIL_HOST_USER'
    # # message =  f"""<strong>{event_type}</strong> request by <strong>{person_name}</strong> for <strong>{date_start}</strong> has been submitted and is pending approval.\n\n
    # # click here to see the request: http://pupper1n0.pythonanywhere.com/scheduler/ \n\n
    # # Otherwise, click here to quick approve http://pupper1n0.pythonanywhere.com/quick-approve/{obj.pk}\n
    # # TEMP: http://127.0.0.1:8000/quick-approve/{obj.pk}\n\n
    # # Thank you,\nScheduler"""
    # to_email = ['elbouni.wassem@gmail.com']     # Will be changed to the email of the person in charge of approving events
    # send_mail(
    #     subject,
    #     plain_message,
    #     from_email,
    #     to_email,
    #     html_message=html_message,
    #     fail_silently=False,
    # )

    return redirect(reverse('scheduler:index'))


def quick_approve(request, pk):
    event = Event.objects.get(id=pk)
    # event.status = "A"
    # event.save()
    # return redirect(reverse('scheduler:index'))

    if event.status != "A":
        if event.type == "RTO":
            person = Person.objects.get(id=event.person.id)
            if person.RTO_days <= 0:
                return HttpResponseBadRequest("RTO days are already 0")
            person.RTO_days = person.RTO_days - 1
            person.save()
        event.status = "A"
        event.save()
    else:
        return redirect(reverse('scheduler:index')) 


def quick_reject(request, pk):
    event = Event.objects.get(id=pk)
    if event.status == "P":
        event.status = "R"
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
        if obj.status == "P":
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


def login_view(request):
    return render(request, 'scheduler/login.html')


def logout_view(request):
    logout(request)
    return redirect(reverse('scheduler:index'))



def reset_password(request):
    return render(request, 'scheduler/reset_password.html')

def get_random_string(length):
        # With combination of lower and upper case
        result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
        # print random string
        return result_str

def email_reset_form(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.get(email=email)
        new_password = get_random_string(12)
        user.set_password(new_password)
        user.save()
        subject = 'Password reset form'
        from_email = 'settings.EMAIL_HOST_USER'
        message =  f"""Dear {user.first_name}\n\nYou've requested to reset your password. Please click the link below to set a new password:\n
        \n\nhttp://pupper1n0.pythonanywhere.com/reset-password-form/{user.pk}/{new_password}/\n\nIf this action was not made by you, please ignore this email.\n\nBest regards,\nNEScheduler
        """
        to_email = [email]
        send_mail(
            subject,
            message,
            from_email,
            to_email,
            fail_silently=False,
        ) 
    return redirect(reverse('scheduler:login_view'))


def new_password_form(request, pk, passwd):
    user = User.objects.get(id=pk)
    print(user.password)
    # print(user.check_password(passwd))
    print(authenticate(request, username=user.username, password=passwd))

    if user.check_password(passwd):
        context = {'user': user}
        return render(request, 'scheduler/new_password_form.html', context=context)
    return HttpResponseBadRequest("Invalid link")



def reset_password_and_redirect(request):
    if request.method == "POST":
        user_id = request.POST.get('username')
        new_password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        if new_password != password_confirm:
            return HttpResponseBadRequest("Passwords do not match")
        user = User.objects.get(username=user_id)
        user.set_password(new_password)
        user.save()
        return redirect(reverse('scheduler:login_view'))