from django.contrib import admin
from django.urls import path
from .views import *
from .views import Upload

urlpatterns = [
    # API to post comment
    # path('admin/', admin.site.urls),
    path("", feed, name="feed"),
    path("upload/", Upload, name="upload"),
    path('delete/<int:serial_no>/', delete_upload, name='delete_upload'),
]
