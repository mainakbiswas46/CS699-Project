from django.contrib import admin
from .models import Question, Answer

# Register your models here.
class UploadQuestion(admin.ModelAdmin):
    exclude = ("slug", "author")


admin.site.register(Question, UploadQuestion)
admin.site.register(Answer)
# admin.site.register((Question, Answer))
