from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_review_to_cloudant
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import random

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def get_random_cars():
    makes = ["Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes", "Audi", "Volkswagen", "Hyundai"]
    models = ["ModelA", "ModelB", "ModelC", "ModelD", "ModelE", "ModelF", "ModelG", "ModelH", "ModelI", "ModelJ"]
    years = list(range(2000, 2023))
    
    cars = []
    for _ in range(3):
        car = {
            "make": random.choice(makes),
            "model": random.choice(models),
            "year": random.choice(years)
        }
        cars.append(car)
    
    return cars

def about(request):
    return render(request, 'djangoapp/about.html')


def contact(request):
    return render(request, 'djangoapp/contact.html')

def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'djangoapp/index.html')

def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

def registration_request(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
        user.save()
        return redirect('djangoapp:index')
    return render(request, 'djangoapp/registration.html')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    dealerships = get_dealers_from_cf('https://asifmahsud54-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/dealership')
    context = {'dealership_list': dealerships}
    return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    dealer_reviews = get_dealer_reviews_from_cf('https://asifmahsud54-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/review', dealer_id)
    context = {'reviews': dealer_reviews, 'dealer_id': dealer_id}
    return render(request, 'djangoapp/dealer_details.html', context)

def add_review(request, dealer_id):
    if request.method == "GET":
        cars = get_random_cars()
        context = {'cars': cars, 'dealer_id': dealer_id}
        return render(request, 'djangoapp/add_review.html', context)
    
    elif request.method == "POST":
        # Extract data from the form
        content = request.POST.get('content')
        purchasecheck = request.POST.get('purchasecheck') == 'on'
        car = request.POST.get('car')
        purchasedate = request.POST.get('purchasedate')
        
        payload = {
                "car": car,
                "dealership": 1,
                "purchase": purchasecheck,
                "purchase_date": datetime.strptime(purchasedate, '%m/%d/%Y').isoformat(),
                "review": content
            }

        response = post_review_to_cloudant(**payload)

        if response.status_code == 201:
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
        else:
            return HttpResponse(response.status_code, status=400)
