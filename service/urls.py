from django.urls import path
from . import views


urlpatterns = [
    path('', views.mainView, name = 'mainView'),

    # clustering url, ajax
    path('cluster/', views.cluster, name = 'cluster'),
    path('cluster/ajax', views.clusterAjax, name = 'clusterajax'),

    path('ingredient/', views.ingredient, name = 'ingredient'),


    # image url, ajax, cnn
    path('image/', views.image, name = 'image'),
    path('image/ajax', views.imageAjax, name = 'imageAjax'),
    path('image/cnn', views.cnnModel, name = 'cnnModel'),

    #file Download
    path('downloadFile/', views.downloadFile, name = 'downloadFile'),




    path('changeImage/', views.changeImage, name = 'changeImage'),
    path('changeImage/ajax', views.changeImageAjax, name = 'changeImageAjax'),


    path('tech/', views.tech, name = 'tech'),

    #barlocation
    path('barLocation/', views.barLocation, name = 'barLocation'),
    path('barLocation/geoInfo', views.barLocationInfo, name = 'geoInfo'),


    # maptest
    path('maptest/', views.maptest, name = 'maptest'),

]