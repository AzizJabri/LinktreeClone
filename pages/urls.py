from cgitb import handler
from django.urls import path
from .views import *


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path("dashboard/", Dashboard.as_view(), name="dashboard"),
    path("page/create/", PageCreate.as_view(), name="page_create"),
    path("<slug:slug>/", PageView.as_view(), name="page_detail"),
    path("<slug:slug>/update/", PageUpdate.as_view(), name="page_update"),
    path("<slug:slug>/delete/", PageDelete.as_view(), name="page_delete"),
    path("<slug:slug>/customize/", PageCustomize.as_view(), name="page_customize"),
    path("<slug:slug>/link/create/", LinkCreate.as_view(), name="link_create"),
    path("<slug:slug>/link/<int:id>/update/",
         LinkUpdate.as_view(), name="link_update"),
    path("<slug:slug>/link/<int:id>/delete/",
         LinkDelete.as_view(), name="link_delete"),
    path("<slug:slug>/link/<int:id>/view/",
         LinkView.as_view(), name="link_view"),
    path("<slug:slug>/link/<int:id>/customize/",
         LinkCustomize.as_view(), name="link_customize"),
]
