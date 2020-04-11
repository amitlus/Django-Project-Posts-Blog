
from django.contrib import admin
from django.urls import path, include
from TheApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('TheApp/', include('TheApp.urls')),
    path('logout/', views.user_logout, name='logout'),


]
