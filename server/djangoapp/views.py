from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from.models import CarMake, CarModel
from.restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)

@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    response_data = {"userName": username}
    if user is not None:
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(response_data)

def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except:
        logger.debug("{} is new user".format(username))
    if not username_exist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)

def get_cars(request):
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()
    car_makes = CarMake.objects.select_related('car_model')
    cars = []
    for car_make in car_makes:
        for car_model in car_make.car_model.all():
            cars.append({"CarModel": car_model.name, "CarMake": car_make.name})
    return JsonResponse({"CarModels": cars})

def initiate():
    car_make_data = [
        {"name": "NISSAN", "description": "Great cars. Japanese technology"},
        {"name": "Mercedes", "description": "Great cars. German technology"},
        {"name": "Audi", "description": "Great cars. German technology"},
        {"name": "Kia", "description": "Great cars. Korean technology"},
        {"name": "Toyota", "description": "Great cars. Japanese technology"},
    ]
    car_make_instances = []
    for data in car_make_data:
        car_make_instances.append(CarMake.objects.create(name=data['name'], description=data['description']))
    car_model_data = [
        {"name": "Pathfinder", "type": "SUV", "year": 2021, "car_make": car_make_instances[0]},
        {"name": "Qashqai", "type": "SUV", "year": 2021, "car_make": car_make_instances[0]},
        {"name": "XTRAIL", "type": "SUV", "year": 2021, "car_make": car_make_instances[0]},
        {"name": "A-Class", "type": "SUV", "year": 2021, "car_make": car_make_instances[1]},
        {"name": "C-Class", "type": "SUV", "year": 2021, "car_make": car_make_instances[1]},
        {"name": "E-Class", "type": "SUV", "year": 2021, "car_make": car_make_instances[1]},
        {"name": "A4", "type": "SUV", "year": 2021, "car_make": car_make_instances[2]},
        {"name": "A5", "type": "SUV", "year": 2021, "car_make": car_make_instances[2]},
        {"name": "A6", "type": "SUV", "year": 2021, "car_make": car_make_instances[2]},
        {"name": "Sorrento", "type": "SUV", "year": 2021, "car_make": car_make_instances[3]},
        {"name": "Carnival", "type": "SUV", "year": 2021, "car_make": car_make_instances[3]},
        {"name": "Cerato", "type": "Sedan", "year": 2021, "car_make": car_make_instances[3]},
        {"name": "Corolla", "type": "Sedan", "year": 2021, "car_make": car_make_instances[4]},
        {"name": "Camry", "type": "Sedan", "year": 2021, "car_make": car_make_instances[4]},
        {"name": "Kluger", "type": "SUV", "year": 2021, "car_make": car_make_instances[4]},
    ]
    for data in car_model_data:
        CarModel.objects.create(name=data['name'], car_make=data['car_make'], type=data['type'], year=data['year'])

#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

def get_dealer_reviews(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})