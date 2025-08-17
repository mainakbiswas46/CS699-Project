from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=100, default="")
    lname = models.CharField(max_length=100, default="")
    email = models.EmailField(max_length=100, default="")
    # roll_number = models.CharField(max_length=12, default="")
    college_name = models.CharField(max_length=255, default="")
    phone_number = models.CharField(max_length=10, default="")
    branch = models.CharField(
        max_length=4,
        choices=[
            ("CSE", "CSE"),
            ("ECE", "ECE"),
            ("EE", "EE"),
            ("ME", "ME"),  
            ("CE", "CE"),
        ],
        default="CSE",
    )
    year = models.CharField(max_length=4, default="")
    profile_pic = models.ImageField(null=True, blank=True, upload_to="profile_pics/")
    auth_token = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    safe_mode = models.BooleanField(default=True)
    attempts = models.IntegerField(default=3)
    next_attempt = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
