from django.shortcuts import render
from django.http import HttpResponse
from .models import Event, Person, Boutique, ShiftCover
from django.shortcuts import redirect
from django.urls import reverse
from datetime import datetime, timedelta
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import random
import string

from django.core import serializers

# Maximum number of rtos per day by position and date
MG_RTO_MAX = 1
TL_RTO_MAX = 1
CS_RTO_MAX_MON_THR = 2
CS_RTO_MAX_FRI_SUN = 1
SS_RTO_MAX = 1


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def home(request):
    context = {'boutiques': Boutique.objects.all()}
    return render(request, 'scheduler/home.html', context=context)

# Create your views here.
def index_view(request, pk):
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return HttpResponseBadRequest("Invalid username or password")

    events = Event.objects.all().filter(boutique__id=pk)
    shift_covers = ShiftCover.objects.all().filter(boutique__id=pk)

    events_json = []

    for i in events:
        if i.type == "RTO":
            events_json.append({
                "title": i.person.f_name + " RTO",
                "type": i.type,
                "date": i.date.strftime("%Y-%m-%d"),
                "color": "orange",
                "id": i.id,
                "person": i.person.f_name,
                "comment": i.comment
            })
        elif i.type == "OTH":
                events_json.append({
                "title": i.person.f_name,
                "type": i.type,
                "date": i.date.strftime("%Y-%m-%d"),
                "color": "#1d9978",
                "id": i.id,
                "person": i.person.f_name,
                "comment": i.comment
            })
        else:
            events_json.append({
                "title": i.person.f_name + " Vacation",
                "type": i.type,
                "date": i.date.strftime("%Y-%m-%d"),
                "color": "blue",
                "id": i.id,
                "person": i.person.f_name,
                "comment": i.comment
            })
        if i.status =='P':
            events_json[-1]["color"] = "gray"
        elif i.status =='R':
            events_json[-1]["color"] = "blue"
    #
    for i in shift_covers:
                events_json.append({
                "title": f"{i.covering_person.f_name} Covered {i.original_person.f_name}",
                "type": "SWP",
                "date": i.date.strftime("%Y-%m-%d"),
                "color": "purple",
                "id": i.id,
            })


    serialized_people = Person.objects.all().values()
    serialized_people = serializers.serialize('json', Person.objects.all().order_by('f_name'))
    people = Person.objects.all().filter(boutique__id = pk).order_by('f_name')
    boutique = Boutique.objects.get(id=pk)

    context = {"people" : people, "events": events_json, "serialized_people":serialized_people, "boutique":boutique}

    return render(request, "scheduler/index.html", context)
    # return HttpResponse("Hello, world. You're at the scheduler index.")



# Helper function that returns a list of dates between start_date and end_date
def get_dates_between(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    date_list = []

    while start_date <= end_date:
        date_list.append(start_date.strftime("%Y-%m-%d"))
        start_date += timedelta(days=1)

    return date_list


def approved_rto_event_creator(person, date, boutique, comment):
    event = Event(person=person, date=date, type="RTO", boutique=boutique, comment=comment)
    event.save()
    person.RTO_days -= 1
    person.save()



def create_event(request):
    if request.method != 'POST':
        return redirect(reverse('scheduler:home'))

    person_name = request.POST.get('person')
    event_type = request.POST.get('options-outlined')
    date = request.POST.get('date')
    date = datetime.strptime(date, "%Y-%m-%d")
    comment = request.POST.get('comment')


    boutique_id = request.POST.get('boutique_id')
    try: # Check if the person exists
        person = Person.objects.get(f_name=person_name)
    except Person.DoesNotExist:
        return redirect(reverse('scheduler:index', args=[boutique_id]))


    # Check if the person already has an event on that day
    events = Event.objects.filter(date=date)
    boutique = Boutique.objects.get(id=boutique_id)

    if events.filter(person__f_name=person_name).exists(): # If the person already has an event on that day
        return HttpResponseBadRequest("Person already has an event on that day")
    
    # Get the number of RTOs for that day and position
    total_rto_events = events.filter(type="RTO").count()
    tl_rto_events = events.filter(type="RTO", person__position="TL", boutique__id = boutique_id).count()
    cs_rto_events = events.filter(type="RTO", person__position="CS", boutique__id = boutique_id).count()
    ss_rto_events = events.filter(type="RTO", person__position="SS", boutique__id = boutique_id).count()
    mg_rto_events = events.filter(type="RTO", person__position="MG", boutique__id = boutique_id).count()
    
    

    # Check if the person has reached the maximum number of RTOs for that day and position
    if event_type == "RTO" or event_type == "MTO":
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
        
        if event_type == "MTO":
            start_date_loop = request.POST.get('start-date')
            end_date_loop = request.POST.get('end-date')
            difference_in_days = get_dates_between(start_date_loop, end_date_loop)

            for date in difference_in_days:
                approved_rto_event_creator(person, date, boutique, comment)

        else:
            Event.objects.create(person=person, type="RTO", date=date, status="P", boutique=boutique, comment=comment)
        context = {
            "person": person_name,
            "event_type": event_type,
            "date": date,
        }
    elif event_type == "SWP":
        try:
            covering_person = Person.objects.get(f_name=request.POST.get('shift-covering-person'))
        except Person.DoesNotExist:
            return redirect(reverse('scheduler:index', args=[boutique_id]))
        ShiftCover.objects.create(original_person=person, covering_person=covering_person, date=date, boutique=boutique, comment=comment)
    elif event_type == "OTH":
        Event.objects.create(person=person, type="OTH", date=date, status="O", boutique=boutique, comment=comment)

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

    return redirect(reverse('scheduler:index', args=[boutique_id]))


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
        return redirect(reverse('scheduler:index', args=[event.boutique.id])) 


def quick_reject(request, pk):
    event = Event.objects.get(id=pk)
    if event.status == "P":
        event.status = "R"
        event.save()
    return redirect(reverse('scheduler:index', args=[event.boutique.id])) 
    


def delete_event(request, pk):
    event = Event.objects.get(id=pk)
    if request.method == 'POST':
        event.delete()
        return redirect(reverse('scheduler:index', args=[event.boutique.id]))


def set_event_status(request):
    if request.method == 'POST':
        # print("HI")
        event_id = request.POST.get('event_id')
        status = request.POST.get('status')
        event = Event.objects.get(id=event_id)
        # Perform actions based on the status value
        if event.status == "P":
            if status == 'A' and event.status != "A":
                if event.type == "RTO":
                    person = Person.objects.get(id=event.person.id)
                    person.RTO_days = person.RTO_days - 1
                    person.save()
                event.status = "A"
                event.save()
            elif status == 'R':
                event.status = "R"
                event.save()
            elif status == 'D':
                event.delete()
        return redirect(reverse('scheduler:index', args=[event.boutique.id]))



def redirect_index(request):
    return redirect(reverse('scheduler:home'))


def login_view(request, pk):
    return render(request, 'scheduler/login.html')


def logout_view(request):
    logout(request)
    return redirect(reverse('scheduler:home'))



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