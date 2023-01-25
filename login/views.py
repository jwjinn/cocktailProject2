import argon2.exceptions
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import JsonResponse
from argon2 import PasswordHasher
from login.models import *


from collections import OrderedDict
import json

# Create your views here.
# https://arotein.tistory.com/22

def index(request):

    if request.method == 'GET':
        return render(request, 'index.html')

    if request.method == 'POST':

        email = request.POST['email']
        password = request.POST['password']

        print(email)
        print(password)


        login = Userregister.objects.filter(email=email)

        if( not login.exists()):
            print("아이다가 없다.")
            return redirect('index')


        dbPassword = login.values()[0]['password']

        try:
            if (PasswordHasher().verify(dbPassword, password)):
                print("비밀번호 일치한다.")

                request.session['email'] = email
                """
                최초로 세션을 사용을 할려면, migrate를 해야 한다.
                
                python manage.py makemigrations
                python manage.py migrate
                
                """

                return redirect('service/')

        except argon2.exceptions.VerifyMismatchError as e:
            print("비밀번호 일치 안함.")
            return redirect('index')


        return redirect('index')



def register(request):

    if request.method == 'GET':
        return render(request, 'register.html')

    if request.method == 'POST':
        email = request.POST['email']
        password = PasswordHasher().hash(request.POST['password'])
        name = request.POST['name']
        gender = request.POST['gender']
        age = int(request.POST['age'])
        phone_number = request.POST['phone_number']
        hadoopLocation = "/user/"+email+"/photo"

        register = Userregister(email= email, password= password, name=name,
                                gender=gender, age=age, phone_number=phone_number, hadooplocation=hadoopLocation)

        register.save()


        # print(hadoopLocation)
        #
        # #https://computer-science-student.tistory.com/407
        # #fs = FileSystemStorage(location='/home/joo/images', base_url='/home/joo/images')
        #
        # dict = {'email': email,
        #         'hadoop': hadoopLocation}
        #
        # with open('/home/joo/hadoopLocation/test.json', 'w') as f:
        #      json.dump(dict, f)

        """
        json 파일의 갱신
        """

        # with open('/home/joo/hadoopLocation/test.json') as f:
        #     d_update = json.load(f, object_pairs_hook = OrderedDict)
        #
        # print("기존: " + d_update)




        return redirect('index')


def logout(request):
    request.session.flush()
    return redirect('index')

