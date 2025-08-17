from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.


class Question(models.Model):
    serial_no = models.AutoField(
        primary_key=True
    )  # primary_key = True --> Increment Automatically
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    subject = models.CharField(max_length=100, null=True)
    tags = models.CharField(max_length=40, null=True, blank=True)
    timestamp = models.DateTimeField(blank=True)
    edited = models.BooleanField(default=False)
    edited_timestamp = models.DateTimeField(blank=True, null=True)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    dislikes = models.ManyToManyField(User, related_name="dislikes", blank=True)
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
    total_answers = models.IntegerField(default=0)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def split_tags(self):
        if self.tags:
            return self.tags.split(",")
        return []

    def __str__(self):
        return str(self.serial_no) + ". " + self.title + " - " + self.author


class Answer(models.Model):
    serial_no = models.AutoField(
        primary_key=True
    )  # primary_key = True --> Increment Automatically
    comment = models.TextField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # on_delete=models.CASCADE --> Delete all the comments of the user if the user is deleted
    post = models.ForeignKey(
        Question, on_delete=models.CASCADE
    )  # on_delete=models.CASCADE --> Delete all the comments of the post if the post is deleted
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True
    )  # self --> Refering a blog comment(reply) or, 1st Comment The same table
    timestamp = models.DateTimeField(default=now)
    edited = models.BooleanField(default=False)
    edited_timestamp = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return (
            "Post: "
            + str(self.post)
            + " - Comment: "
            + str(self.serial_no)
            + " - by "
            + self.user.username
        )


# Post = Question
# BlogComment = Comment
