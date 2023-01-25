import json
import os.path

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from service.models import Uploadimage, Uploadimagelog
from datetime import datetime
from pytz import timezone
from django.utils import timezone

import os
from django.http import FileResponse

import elasticsearch
from elasticsearch import helpers, Elasticsearch
import csv
import pandas as pd
import numpy as np
import json

# gan 모델 임포트관련

from ganClass import *

# cnn 모델 임포트관련

from cnnClass import *

# Create your views here.

# formdata 관련: https://uni2237.tistory.com/10
# 업로드 다운로드 기능: https://triple-f-coding.tistory.com/5
# 파일 다운로드 기능 https://wonpaper.tistory.com/466

# 다운 로드: https://hyundy.tistory.com/11


"""
service/index에서
True를 리턴할 경우에, '로그아웃' 버튼이 생기기 위해서.
False를 리턴할 경우에, 현재 접속 아이디를 html에서 표현 가능하도록.

"""


## 로그인 로그아웃 기능.
def logInOut(request):
    context = {}

    login_session = request.session.get("email", "")

    if login_session == "":
        context["login_session"] = False

    else:
        # 값이 있으면,
        context["login_session"] = True
        context["email"] = request.session["email"]

        # print(login_session['email'])
        # context['email'] = login_session['email']

    return context


"""
service/index에서
리턴 False이면, index로 리다이렉트가 되도록.

"""


## 로그인 확인
def logInCheck(request):
    login_session = request.session.get("email", "")

    if login_session == "":
        # print("session에 저장된 아이디가 없습니다.")
        return False

    else:
        return True


# 메인화면
def mainView(request):
    if logInCheck(request):
        context = logInOut(request)
        print(request.session["email"])

        return render(request, "service/index.html", context)
    else:
        # print('비정상적인 접근: session에 id가 없다.')
        return redirect("/")


# clustering - es


def search_django(keyword):
    es = Elasticsearch("http://chae2:chae1234@34.64.247.4:9200")
    index = "cktl_info_all"
    body = {"query": {"match": {"name": {"query": keyword}}}}
    res = es.search(index=index, body=body)
    return res["hits"]


#     es = Elasticsearch("http://ID:PW@34.64.197.249:9200")


def search_django2(keyword):
    es = Elasticsearch("http://chae2:chae1234@34.64.247.4:9200")
    index = "cktl_info_all"
    body = {"query": {"match_phrase": {"name": {"query": keyword}}}}
    res = es.search(index=index, body=body)
    return res["hits"]


# r"C:\Users\Luna\Desktop\DATA-WEB\static\csv\gower_df.csv"


def gower(keyword):
    # df = pd.read_csv("static\csv\gower_df.csv")
    df = pd.read_csv("static/csv/gower_df.csv")

    temp = df[keyword].sort_values(ascending=True)[:5].index
    search_series = df.iloc[temp]["name"]
    search_list = search_series.to_list()
    return search_list


# 내가 마신 칵테일과 비슷한 칵테일은?
def cluster(request):
    if logInCheck(request):
        print("현재 로그인 이메일 " + request.session["email"])
        return render(request, "service/cluster.html")
    else:
        print("비정상적인 접근: session에 id가 없다.")
        return redirect("/")


# 비슷한 칵테일 추천
def clusterAjax(request):
    key = request.build_absolute_uri().split("?")
    print(key[1])
    try:
        target = gower(search_django(key[1])["hits"][0]["_source"]["name"])
    except IndexError:
        target = {}
    print(target)

    temp = {}
    counter = 0
    try:
        for i in target[1:]:
            temp["item" + str(counter)] = search_django2(i)["hits"][0]["_source"]
            counter += 1
    except TypeError:
        temp = {}
    print(temp)
    return JsonResponse(temp)


# 지금 만들 수 있는 칵테일은?
def ingredient(request):
    if logInCheck(request):
        print("현재 로그인 이메일 " + request.session["email"])
        return render(request, "service/ingredient.html")
    else:
        print("비정상적인 접근: session에 id가 없다.")
        return redirect("/")

    # return render(request, 'service/ingredient.html')


# 이 칵테일의 이름은?
def image(request):
    if logInCheck(request):
        print("현재 로그인 이메일 " + request.session["email"])
        return render(request, "service/image.html")
    else:
        print("비정상적인 접근: session에 id가 없다.")
        return redirect("/")

    # return render(request, 'service/image.html')


@csrf_exempt
def imageAjax(request):
    img = request.FILES.get("uploadFile")

    imageName = img.name
    trimImageName = imageName.replace(" ", "")

    email = request.session["email"]
    # day = str(datetime.now(timezone('Asia/Seoul')).date())

    day = str(timezone.now().date())

    dotPosition = trimImageName.find(".")

    hadoopFileName = trimImageName + day

    hadoopFileName = (
            trimImageName[0:dotPosition]
            + "-"
            + day
            + trimImageName[dotPosition: len(trimImageName)]
    )

    uploadImage = Uploadimage(
        email=email,
        filename=trimImageName,
        register_date=day,
        hadoopfilename=hadoopFileName,
    )
    uploadImageLog = Uploadimagelog(
        email=email,
        filename=trimImageName,
        register_date=day,
        hadoopfilename=hadoopFileName,
    )

    uploadImage.save()
    uploadImageLog.save()

    # TODO 서버용 경로와 로컬 테스트 경로를 구분해서 업로드해야 합니다. 깃헙 PUSH시, 서버 경로로.

    """
    하둡 저장용 경로.
    """
    ## 서버용 하둡에 적재할
    # fs = FileSystemStorage(location='/home/jwjinn/attachement/images', base_url='/home/jwjinn/attachement/images')

    ## 로컬 경로(주우진)
    fs = FileSystemStorage(location='/home/joo/images', base_url='/home/joo/images')

    temp = cnnCover()

    temp.setImage(img)

    rankCnn = temp.keyValue()

    # TODO: 이곳에서 엘라스틱과 연결을 할 것, context에 설명을 제조 방법을 추가해서 리턴할

    """
    예시 출력: [('Bramble', 2.0369181632995605), ('Cosmopolitan', 2.0368924140930176), ('Alexander', 1.8241112232208252), ('Kir', 1.7370887994766235)]

    점수 높은 상 위 4개가 리턴된다.것

    칵테일 이름 'Bramble', 'Cosmopolitan'과 같은 이름을 엘라스틱 쿼리에 입력을 해서, 주조방법을 리턴한다.
    """

    print(rankCnn)

    context = {"private": 15,
               "cnnResult": rankCnn}

    fs.save(hadoopFileName, img)
    return JsonResponse(context)


def downloadFile(request):
    email = request.session["email"]

    file_path = os.path.abspath("media/gan/")
    file_name = os.path.basename(f"media/gan/{email}.png")

    fs = FileSystemStorage(file_path)

    response = FileResponse(fs.open(file_name, "rb"), as_attachment=True)

    response["Content-Disposition"] = f'attachment; filename="{email}.png"'

    return response


# 칵테일 사진 화풍변경


def changeImage(request):
    if logInCheck(request):
        print("현재 로그인 이메일 " + request.session["email"])
        return render(request, "service/changeImage.html")
    else:
        print("비정상적인 접근: session에 id가 없다.")
        return redirect("/")

    # return render(request, 'service/changeImage.html')


@csrf_exempt
def changeImageAjax(request):

    print("changeImageAjax 호출")

    email = request.session["email"]

    context = {"private": 15}

    img = request.FILES.get("uploadFile")

    k = cover()

    k.imageLocation(img)

    k.saveLocation(f'{os.getcwd()}/media/gan/{email}.png')
    k.Gan_prc()

    return JsonResponse(context)


# 사용 기술
def tech(request):
    if logInCheck(request):
        print("현재 로그인 이메일 " + request.session["email"])
        return render(request, "service/tech.html")
    else:
        print("비정상적인 접근: session에 id가 없다.")
        return redirect("/")

    # return render(request, 'service/tech.html')


# 주변 칵테일 바의 위치는?
def barLocation(request):
    if logInCheck(request):
        print("현재 로그인 이메일 " + request.session["email"])
        return render(request, "service/barLocation.html")
    else:
        print("비정상적인 접근: session에 id가 없다.")
        return redirect("/")

    # return render(request, 'service/barLocation.html')


def barLocationInfo(request):
    input_val = request.GET.get("input_val")

    print(input_val)

    context = {"test": input_val}

    return JsonResponse(context)


def maptest(request):
    return render(request, "service/maptest.html")


"""
이미지를 모델에 보내고, 설명까지 리턴하는 곳.
"""


@csrf_exempt
def cnnModel(request):
    print("cnnModel 호출.")

    img = request.FILES.get("uploadFile")
    imageName = img.name

    ## 장고 이미지 모델링시 입력될 이미지.
    ## https://chagokx2.tistory.com/62
    djangoFs = FileSystemStorage(location="media", base_url="media")

    print(djangoFs.open(imageName))  # 이미지 호출. 이 경로를 사용 혹은 바로 사용가능하면 사용.

    """
    <example>

    input: djangoFs.open(imageName))

    output: cocktail = ['Alexander', 'Aviation', 'B-52', 'Bacardi']

    """

    cocktail = ["Alexander", "Aviation", "B-52", "Bacardi"]

    """
    모델에서 나온 결과값 cocktail 리스트를 엘라스틱 쿼리로 집어넣는다.

    예시 결과값 howToMake
    """
    howToMake = ["aaaa", "bbbb", "cccc", "dddd"]

    context = {"cnnModel": "cnnModel에서 왔다.", "return": cocktail, "howToMake": howToMake}

    return JsonResponse(context)
