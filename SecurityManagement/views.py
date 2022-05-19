from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .forms import RegisterForm
from .models import ManoUser as User
from django.contrib import auth as Auth
from nssmf.models import ServiceMappingPluginModel, GenericTemplate, SliceTemplate
from django.db.models import Q

import json


def login(request):
    if request.method != "POST":
        return JsonResponse({
            "status": 1,
            "message": "error"
            })
    data = request.body.decode("utf-8")
    data = json.loads(data)
    name = data.get('name')
    password = data.get('password')
    if name == "admin": # 預設管理者
        password = "admin"
        register(request)
    user = Auth.authenticate(username=name, password=password)

    if not user:
        return JsonResponse({
            "status": 1,
            "message": "無此帳號"
            })
    else:
        Auth.login(request, user)
        request.session.create()
        uu_id = user.id
        role = user.role
        if role not in ["tenant", "admin"]:
            rep = JsonResponse({
            "status": 1,
            "message": "該帳號未被授權"
            })
        else:
            rep = JsonResponse({
                "status": 0,
                "message": "登入成功",
                "role": role
                })
            request.session['uu_id'] = uu_id
            rep.set_cookie('uu_id', uu_id)
        return rep

def register(request):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        data = json.loads(data)
        f = RegisterForm(data)
        if f.is_valid():
            name = f.cleaned_data['name']
            password = f.cleaned_data['password']

            if name == "admin": # 預設管理者
                password == "admin"
                if not User.objects.filter(username=name).first():
                    print(3)
                    user_db = User(
                        username=name,
                        role="admin",
                        is_superuser=True,
                        is_staff=True
                    )
                    user_db.set_password(password)
                    user_db.save()
                    return JsonResponse({
                        "status": 0,
                        "message": "註冊成功"
                        })
                
            else:
                if User.objects.filter(username=name).first():
                    return JsonResponse({
                        "status": 1,
                        "message": "使用者名稱重複"
                    })
                user_db = User(
                    username=name,
                    role="unverified"
                )

                user_db.set_password(password)
                user_db.save()
                return JsonResponse({
                    "status": 0,
                    "message": "註冊成功"
                    })

    return JsonResponse({
            "status": 1,
            "message": "no get"
            })

def unverified_list(request):
    name = request.user
    print(name)
    if name not in ["AnonymousUser", "", None]:
        user_obj = User.objects.filter(username=name).first()
        if user_obj:
            uu_id = user_obj.id
            role = user_obj.role
        else:
            return JsonResponse({
                "status": 1,
                "message": "查無使用者"
            })
    else:
        return JsonResponse({
                "status": 1,
                "message": "請先登入"
            })
    if role != "admin":
        return JsonResponse({
                "status": 1,
                "message": "非admin"
            })
    result = User.objects.filter(role="unverified")
    result_data = list()

    for data in result:
        join_time = data.date_joined.strftime("%Y-%m-%d %H:%M")
        login_time = data.last_login.strftime("%Y-%m-%d %H:%M") if data.last_login else None
        result_data.append({
            "id": data.id,
            "username": data.username,
            "join_data": join_time,
            "last_login": login_time,
            "email": data.email
        })

    return JsonResponse({
            "status": 0,
            "data": result_data
            })

def admin_check(request):
    name = request.user
    if name not in ["AnonymousUser", "", None]:
        user_obj = User.objects.filter(username=name).first()
        if user_obj:
            uu_id = user_obj.id
            role = user_obj.role
        else:
            return JsonResponse({
                "status": 1,
                "message": "查無使用者"
            })
    else:
        return JsonResponse({
                "status": 1,
                "message": "請先登入"
            })
    if role != "admin":
        return JsonResponse({
                "status": 1,
                "message": "非admin"
            })

    data = request.body.decode("utf-8")
    data = json.loads(data)
    names = data.get('names')
    for name in names:
        User.objects.filter(username=name).update(role="tenant")
        
    return JsonResponse({
            "status": 0,
            "message": "修改成功"
            })

def get_role(request):
    name = request.user
    if name not in ["AnonymousUser", "", None]:
        user_obj = User.objects.filter(username=name).first()
        if user_obj:
            role = user_obj.role
            return JsonResponse({
                "status": 0,
                "role": role
            })
        else:
            return JsonResponse({
                "status": 1,
                "message": "查無使用者"
            })
    else:
        return JsonResponse({
                "status": 1,
                "message": "請先登入"
            })

def logout(request):
    Auth.logout(request)
    return JsonResponse({
            "status": 0,
            "message": "登出"
            })

def get(request):
    name = request.user
    print(request.session['uu_id'])
    print(name)
    rep = JsonResponse({
            "status": 0,
            "message": "登入成功"
            })
    return rep

def service_plygin_list(request):
    uu_id, role, message = check_user(request)
    if message:
        return JsonResponse({
                "status": 1,
                "message": message
                })
    if role == "admin":
        result = ServiceMappingPluginModel.objects.all()
    else:
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

def generic_list(request):
    uu_id, role, message = check_user(request)
    if message:
        return JsonResponse({
                "status": 1,
                "message": message
                })
    if role == "admin":
        result = GenericTemplate.objects.all()
    else:
        result = GenericTemplate.objects.filter(Q(user_id=uu_id)|Q(share=True))
    result_data = list()
    for a in result:
        result_data.append({
            "owner_id": a.user_id,
            "templateId": a.templateId,
            "templateType": a.templateType,
            "name": a.name,
            "nfvoType": a.nfvoType,
            "templateFile": a.templateFile.name,
            "operationStatus": a.operationStatus,
            "description": a.description,
            "operationTime": a.operationTime,
            "share": a.share
        })
    return JsonResponse({
            "status": 0,
            "data": result_data,
            "uu_id": uu_id
            })

def slice_list(request):
    uu_id, role, message = check_user(request)
    if message:
        return JsonResponse({
                "status": 1,
                "message": message
                })
    if role == "admin":
        result = SliceTemplate.objects.all()
    else:
        result = SliceTemplate.objects.filter(Q(user_id=uu_id)|Q(share=True))
    result_data = list()
    for a in result:
        result_data.append({
            "owner_id": a.user_id,
            "templateId": a.templateId,
            "description": a.description,
            # "nfvoType": a.nfvoType,
            # "genericTemplates": a.genericTemplates,
            # "instanceId": a.instanceId,
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
        plygin_object = ServiceMappingPluginModel.objects.filter(name=name)
        if plygin_object:
            plygin_object.update(share=share)
            return JsonResponse({
                    "status": 0,
                    "message": "修改成功"
                    })
        else:
            return JsonResponse({
                    "status": 1,
                    "message": "檔案不存在"
                    })
    except:
        return JsonResponse({
                "status": 1,
                "message": "修改失敗"
                })

def switch_share_gen(request):
    data = request.body.decode("utf-8")
    data = json.loads(data)
    name = data.get('name')
    share = data.get('share')

    try:
        GenericTemplate.objects.filter(name=name).update(share=share)
        return JsonResponse({
                "status": 0,
                "message": "修改成功"
                })
    except:
        return JsonResponse({
                "status": 1,
                "message": "修改失敗"
                })

def check_user(request):
    name = request.user
    print(name)
    uu_id, role, message = -1, "", ""
    if name not in ["AnonymousUser", "", None]:
        user_obj = User.objects.filter(username=name).first()
        if user_obj:
            uu_id = user_obj.id
            role = user_obj.role
        else:
            message = "查無使用者"
    else:
        message = "請先登入"
    return uu_id, role, message
