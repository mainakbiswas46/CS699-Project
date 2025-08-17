from django.contrib import admin
from .models import UploadFiles

# Register your models here.
class UploadFilesClass(admin.ModelAdmin):
    exclude = ("image_url",)


admin.site.register(UploadFiles, UploadFilesClass)
