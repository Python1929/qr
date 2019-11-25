from django.contrib import admin

from django.conf.urls import url,include
from app import views

# SET THE NAMESPACE!
app_name = 'app'
# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    url(r'^register/$',views.register,name='register'),
    url(r'^userlogin/$',views.userlogin,name='userlogin'),
    url(r'^dashboard/$',views.dashboard,name='dashboard'),
    url(r'^staff/$',views.staff,name='staff'),
    url(r'^contractor/$',views.contractor,name='contractor'),
    url(r'^visitor/$',views.visitor,name='visitor'),
    url(r'^entryexit/$',views.entryexit,name='entryexit'),
    url(r'^qrscanner/$',views.qrscanner,name='qrscanner'),
    url(r'^contractordelete/(?P<contractordelete_id>[0-9]+)/$', views.contractordelete, name='contractordelete'),
    url(r'^visitordelete/(?P<visitordelete_id>[0-9]+)/$', views.visitordelete, name='visitordelete'),
    url(r'^contractoredit/(?P<contractoredit_id>[0-9]+)/$', views.contractoredit, name='contractoredit'),
    url(r'^visitoredit/(?P<visitoredit_id>[0-9]+)/$', views.visitoredit, name='visitoredit'),
    #url(r'^stream_video/$',views.stream_video,name="stream_video"),
    url(r'^stream_video$',views.stream_video,name="stream_video"),
    # url(r'^/(?P<visitordelete_id>[0-9]+)/$', views.visitordelete, name='visitordelete'),





]