from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .forms import RegisterForm
from .models import User
from django.contrib import auth as Auth
from nssmf.models import ServiceMappingPluginModel
from django.db.models import Q

import json


def login(request):
    # root
    # user1234
    if request.method != "POST":
        return JsonResponse({
            "status": 1,
            "message": "error"
            })
    data = request.body.decode("utf-8")
    data = json.loads(data)
    name = data.get('name')
    password = data.get('password')
    user = Auth.authenticate(username=name, password=password)
    request.session.create()
    Auth.login(request, user)

    # user_obj = User.objects.filter(username=name, password=password).first()
    if not user:
        return JsonResponse({
            "status": 1,
            "message": "無此帳號"
            })
    else:
        request.session.create()
        rep = JsonResponse({
            "status": 0,
            "message": "登入成功"
            })
        rep.set_cookie('token', request.session.session_key)
        return rep

def register(request):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        data = json.loads(data)
        f = RegisterForm(data)
        if f.is_valid():
            name = f.cleaned_data['name']
            email = f.cleaned_data['email']
            password = f.cleaned_data['password']
            if User.objects.filter(username=name).first():
                return JsonResponse({
                    "status": 1,
                    "message": "使用者名稱重複"
                })
            user_db = User(
                username=name,
                email=email
            )
            user_db.set_password(password)
            user_db.save()
            return JsonResponse({
                "status": 0,
                "message": "註冊成功"
                })

    return JsonResponse({
            "status": 1,
            "message": "error"
            })

def get(request):
    rep = JsonResponse({
            "status": 0,
            "message": "登入成功"
            })
    return rep

def service_plygin_list(request):
    name = request.user
    if not name:
        return JsonResponse({
            "status": 1,
            "message": "請先登入"
            })
    user_obj = User.objects.filter(username=name).first()
    if not user_obj:
        return JsonResponse({
            "status": 1,
            "message": "查無使用者"
            })
    uu_id = user_obj.id

    result = ServiceMappingPluginModel.objects.filter(Q(user_id=uu_id)|Q(share=True))
    result_data = list()
    for a in result:
        result_data.append({
            "owner_id": a.user_id,
            "allocate_nssi": a.allocate_nssi,
            "deallocate_nssi": a.deallocate_nssi,
            "name": a.name,
            "nfvo_host": a.nfvo_host,
            "nm_host": a.nm_host,
            "pluginFile": a.pluginFile.name,
            "subscription_host": a.subscription_host,
            "share": a.share
        })
    return JsonResponse({
            "status": 0,
            "data": result_data,
            "uu_id": uu_id
            })


def switch_share(request):
    data = request.body.decode("utf-8")
    data = json.loads(data)
    name = data.get('name')
    share = data.get('share')

    try:
        ServiceMappingPluginModel.objects.filter(name=name).update(share=share)
        return JsonResponse({
                "status": 0,
                "message": "修改成功"
                })
    except:
        return JsonResponse({
                "status": 1,
                "message": "修改失敗"
                })




# def get_user(func):
#     def wrapper(*args, **kwargs):
#         print('Hello')
#         return func(*args, **kwargs)
#     return wrapper
