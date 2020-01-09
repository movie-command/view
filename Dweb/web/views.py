from django.shortcuts import render
from django.shortcuts import render, HttpResponseRedirect
from django.contrib import auth
from django.http import HttpResponse
from web.models import User
from web import form as local_form


def index(request):
    user = request.session.get('user', False)
    return render(request, 'index.html', {'user': user})

#显示页面
def registerView(request):
    user = request.session.get('user', False)
    if not user:
        return render(request, 'login.html')
    else :
        return HttpResponseRedirect('/index/')


# 注册
def register(request):
    if request.method == 'POST':
        data = request.POST
        a = local_form.RegisterForm(data)
        if a.is_valid():
            if User.objects.filter(username=data['username']).exists():
                return render(request, 'immediate.html', {'registed': True, 'name': data['username']})
            user = User(**a.cleaned_data)
            user.save()
            return render(request, 'immediate.html', {'name': data['username']})
    return HttpResponseRedirect('/index/')


#登录
def login(request):
    user = request.POST.get('username', None)
    password = request.POST.get('password', None)
    result = User.objects.filter(username=user, password=password)
    if not result:
        return HttpResponse('用户名或者密码不正确')
    else:
       request.session['user'] = user
       #return HttpResponse('登录成功')
       return HttpResponseRedirect('/index/')
#注销
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/index/')
#推荐算法

from web import engine
from web.models import movie,User
import random
#用户信息的推荐
def recommand1(request):
    n1 = User.objects.filter()
    a = len(n1)-1
    n1 = n1[a]
    movi = movie.objects.filter(myear = n1.birthday)
    a = random.randint(0,len(movi))
    mov = movi[a]
    url1 = mov.mpicture
    mov = [str(mov.mname),str(mov.mtype),str(mov.myear),str(mov.mename),str(mov.mdirector)]
    return render(request,'newoold',{"url1":url1,"data":mov})
    # return render(request,'newoold',{'url1'})
#算法的推荐
# def recoommand2(request):
#     a = request.POST.get("a")
#     a = str(a)
#     mov1 = movie.objects.filter(mtype=a)
#     b = random.randint(0,len(mov1))
#     mov1 = mov1[b]
#     mov1 = [str(mov1.mname), str(mov1.mtype), str(mov1.myear), str(mov1.mename), str(mov1.mdirector)]
#     mov1 = movie.objects.filter()
#     return render(request,'newoold',{"data1":mov1})