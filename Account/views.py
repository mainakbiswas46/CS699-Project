from django.shortcuts import redirect, render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from .models import *
from Question.models import *
import uuid
import requests
from better_profanity import profanity
from django.http import HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
import os
from datetime import datetime, timedelta

# Create your views here.
def home(request):
    URL = "https://zenquotes.io?api=random"
    r = requests.get(url=URL)
    data = r.json()
    context = {"quote": data[0]["q"], "author": data[0]["a"]}
    return render(request, "Account/home.html", context)


def handleLogin(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            # email=request.POST.get('email')
            username = request.POST.get("loginusername")
            password = request.POST.get("loginpassword")

            user_obj = User.objects.filter(username=username).first()

            if user_obj is None:
                messages.error(request, "User not found")
                return redirect("/login")
            else:
                profile_obj = Profile.objects.filter(user=user_obj).first()
                attempts = profile_obj.attempts
                if not profile_obj.is_verified:
                    messages.error(
                        request,
                        "Your account is not verified. Please check your mailbox",
                    )
                    return redirect("/login")

                if attempts == 0:
                    time = profile_obj.next_attempt
                    current = datetime.now().replace(tzinfo=None)
                    timeleft = time - current
                    if time > current:
                        min = timeleft.seconds // 60
                        sec = timeleft.seconds % 60
                        messages.error(
                            request,
                            "You have exceeded the maximum number of login attempts. Please wait for "
                            + str(min)
                            + " minutes and "
                            + str(sec)
                            + " seconds before trying again",
                        )
                        return redirect(
                            "/login",
                        )
                    else:
                        profile_obj.attempts = 3
                        profile_obj.next_attempt = None
                        profile_obj.save()

                user = authenticate(request, username=username, password=password)

                if user is not None:
                    login(request, user)
                    return redirect("/")
                else:
                    if attempts == 1:
                        attempts -= 1
                        profile_obj.attempts = attempts
                        profile_obj.next_attempt = datetime.now() + timedelta(minutes=1)
                        profile_obj.save()
                        messages.error(
                            request,
                            "You have exceeded the number of login attempts. Please try again after 10 minutes",
                        )
                        return redirect("/login")
                    else:
                        attempts -= 1
                        profile_obj.attempts = attempts
                        profile_obj.save()
                        messages.error(
                            request, f"Invalid credentials! {attempts} attempts left"
                        )

                    return redirect("/login")

        return render(request, "Account/login.html")


def handleSignup(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST["username"]
            fname = request.POST["fname"]
            lname = request.POST["lname"]
            email = request.POST["email"]
            pass1 = request.POST["pass1"]
            pass2 = request.POST["pass2"]

            college_name = request.POST["college_name"]
            phone_number = request.POST["phone_number"]
            branch = request.POST["branch"]
            year = request.POST["year"]

            try:
                # Username
                if User.objects.filter(username=username).exists():
                    messages.error(request, "Username already exists")
                    return redirect("/signup")

                if not username.isalnum():
                    messages.error(
                        request, "Username should only contains letters & numbers"
                    )
                    return redirect("/signup")

                if len(username) > 10:
                    messages.error(request, "Username must be under 10 characters")
                    return redirect("/signup")

                # First name
                if not fname.isalpha():
                    messages.error(request, "first name must contain only characters")
                    return redirect("/signup")

                # Last name
                if not lname.isalpha():
                    messages.error(request, "Last name must contain only characters")
                    return redirect("/signup")

                # Email
                if User.objects.filter(email=email).exists():
                    messages.success(request, "Email already exists")
                    return redirect("/signup")

                if not email.endswith("@gmail.com"):
                    messages.error(request, "Email must be a gmail account")
                    return redirect("/signup")

                # Password
                if pass1 != pass2:
                    messages.error(request, "Passwords do not match")
                    return redirect("/signup")
                if len(pass1) < 5:
                    messages.error(request, "Password is too short")
                    return redirect("/signup")

                college_name = college_name.title()
                
                # Create User
                user_obj = User.objects.create_user(
                    username=username, email=email, password=pass1
                )
                user_obj.first_name = fname
                user_obj.last_name = lname
                user_obj.save()

                auth_token = str(uuid.uuid4())
                # Create Profile

                profile_obj = Profile.objects.create(
                    user=user_obj,
                    fname=fname,
                    lname=lname,
                    email=email,
                    college_name=college_name,
                    phone_number=phone_number,
                    branch=branch,
                    year=year,
                    auth_token=auth_token,
                    safe_mode=True,
                )
                profile_obj.save()

                send_authentication_mail(username, email, auth_token)
                # messages.success(request, 'Please check your email to verify your account')
                return redirect("/token")

            except Exception as e:
                print(e)
        # else:
        #     return HttpResponse('404 - Not Found')

        # print("POST")
        # print(request.POST)
        # return render(request, 'Account/success.html')
        return render(request, "Account/signup.html")


def token(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "Account/token.html")


def success(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "Account/success.html")


def send_authentication_mail(username, email, auth_token):
    subject = "Verify your Gurukul Account"
    message = f"Hi {username}, \n\t Thanks for getting started with Gurukul!\nWe need a little more information to complete your registration, including a confirmation of your email address. \n\nClick below to confirm your email address:\n\n{settings.BASE_URL}/verify/{auth_token} \n\nIf you have problems, please paste the above URL into your web browser.\n\nWelcome to Gurukul! \nTeam Gurukul"
    from_email = settings.EMAIL_HOST_USER
    to_list = [email]
    print(
        f"From: {from_email},\nTo: {to_list},\nSubject: {subject},\nMessage: {message}, "
    )
    send_mail(subject, message, from_email, to_list, fail_silently=False)


def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, "Account already verified")
                return redirect("/login")
            else:
                profile_obj.is_verified = True
                profile_obj.save()
                messages.success(request, "Your account has been verified successfully")
                return redirect("/login")
        else:
            return redirect("/error")
    except Exception as e:
        print(e)
        messages.success(request, "Something went wrong")


def error(request):
    return render(request, "Account/error.html")


@login_required(login_url="/login")
def handleLogout(request):
    # With Proper Authentication
    if request.method == "GET":
        logout(request)
        messages.success(request, "You are now logged out")
        return redirect("home")
    # Means Direct Site Access
    return HttpResponse("404 - Not Found")


@login_required(login_url="/login")
def search(request):
    query = request.GET["query"]
    # Very long query
    if len(query) > 78:
        allposts = Question.objects.none()
    # Else
    else:
        allposts_Title = Question.objects.filter(
            title__icontains=query, branch=request.user.profile.branch
        )  # .objects --> Get all the objects from the database
        allposts_Tags = Question.objects.filter(
            tags__icontains=query, branch=request.user.profile.branch
        )
        allposts_Subject = Question.objects.filter(
            subject__icontains=query, branch=request.user.profile.branch
        )
        allposts = allposts_Title | allposts_Tags | allposts_Subject
        allposts = allposts.order_by("-timestamp")
        # Union --> Get all the objects from the database
    if allposts.count() == 0:
        messages.warning(request, "No search results found. Please refine your search.")
    user = request.user
    CSEsubjects = [
        "Engineering Mathematics",
        "Discrete Mathematics",
        "Programming in C",
        "Data Structure & Algorithm",
        "Digital Logic",
        "Computer Organisation",
        "Computer Architecture",
        "Operating System",
        "Compiler Design",
        "Database Managment System",
        "Computer Networks",
        "Others",
    ]
    EEsubjects = [
        "Engineering Mathematics",
        "Electric Circuits",
        "Electromagnetic Fields",
        "Signals and Systems",
        "Electrical Machines",
        "Power Systems",
        "Control Systems",
        "Electrical and Electronic Measurements",
        "Analog and Digital Electronics",
        "Power Electronics",
        "Others",
    ]
    ECEsubjects = [
        "Engineering Mathematics",
        "Network Signals & Systems",
        "Electronic Devices",
        "Analog Circuits",
        "Digital Circuits",
        "Control Systems",
        "Communications",
        "Electromagnetics",
        "Others",
    ]
    MEsubjects = [
        "Engineering Mathematics",
        "Strength of Materials",
        "Fluid Mechanics",
        "Thermodynamics",
        "Mechanical Vibrations",
        "Theory of Machines",
        "Manufacturing Processes",
        "Heat Transfer",
        "Engineering Mechanics",
        "Production and Industrial Engineering",
        "Industrial Engineering",
        "Materials Science",
        "Others",
    ]
    CEsubjects = [
        "Engineering Mathematics",
        "Structural Analysis",
        "Fluid Mechanics",
        "Geotechnical Engineering",
        "Transportation Engineering",
        "Environmental Engineering",
        "Surveying",
        "Building Materials",
        "Construction Materials and Management",
        "Hydrology and Water Resources",
        "Solid Mechanics",
        "Others",
    ]

    profile = Profile.objects.filter(user=user).first()

    if not user.is_staff:
        if profile.branch == "EE":
            subjects = EEsubjects
        elif profile.branch == "ECE":
            subjects = ECEsubjects
        elif profile.branch == "ME":
            subjects = MEsubjects
        elif profile.branch == "CE":
            subjects = CEsubjects
        else:
            subjects = CSEsubjects
    else:
        subjects = CSEsubjects
    allposts = allposts.filter(subject__in=subjects)
    allposts = allposts.filter(branch=profile.branch)
    allposts = allposts.order_by("-timestamp")
    if profile.safe_mode:
        for post in allposts:
            profanity.load_censor_words()
            post.title = profanity.censor(post.title)
            post.content = profanity.censor(post.content)
            post.tags = profanity.censor(post.tags)
    params = {"allposts": allposts, "query": query, "subjects": subjects}
    return render(request, "Account/search.html", params)
    # return HttpResponse('Search')


@login_required(login_url="/login")
def user(request):
    if request.method == "POST":
        username = request.POST["username"]
        user = User.objects.filter(username=username).first()
        if user:
            profile = Profile.objects.filter(user=user).first()
            if profile:
                questions = Question.objects.filter(author=user)
                if profile.safe_mode:
                    for q in questions:
                        profanity.load_censor_words()
                        q.title = profanity.censor(q.title)
                answers = Answer.objects.filter(user=user)
                reply_questions = []
                for answer in answers:
                    question = Question.objects.filter(serial_no=answer.post_id).first()
                    if profile.safe_mode:
                        profanity.load_censor_words()
                        question.title = profanity.censor(question.title)
                    if question not in reply_questions:
                        reply_questions.append(question)
                params = {
                    "user": user,
                    "profile": profile,
                    "questions": questions,
                    "answers": answers,
                    "reply_questions": reply_questions,
                }
                return render(request, "Account/user.html", params)
    return redirect("/error")


@login_required(login_url="/login")
def profile(request):
    if request.method == "GET":
        username = request.GET["username"]
        user = User.objects.filter(username=username).first()
        if user:
            profile = Profile.objects.filter(user=user).first()
            questions = Question.objects.filter(author=user)
            if profile.safe_mode:
                for q in questions:
                    profanity.load_censor_words()
                    q.title = profanity.censor(q.title)
            answers = Answer.objects.filter(user=user)
            reply_questions = []
            for answer in answers:
                question = Question.objects.filter(serial_no=answer.post_id).first()
                if profile.safe_mode:
                    profanity.load_censor_words()
                    question.title = profanity.censor(question.title)
                if question not in reply_questions:
                    reply_questions.append(question)
            params = {
                "user": user,
                "profile": profile,
                "questions": questions,
                "answers": answers,
                "reply_questions": reply_questions,
            }
            return render(request, "Account/profile.html", params)
    return redirect("/error")


# def terms_and_conditions(request):
#     return render(request, "Account/terms_and_conditions.html")


@login_required(login_url="/login")
def edit_profile(request):
    if request.method == "POST":
        user_obj = request.user
        college_name = request.POST["college_name"]
        branch = request.POST["branch"]
        year = request.POST["year"]
        user_id = user_obj.id

        profile_obj = Profile.objects.filter(user_id=user_id).first()
        if college_name == "":
            college_name = profile_obj.college_name
        if branch == "":
            branch = profile_obj.branch
        if year == "":
            year = profile_obj.year
        profile_obj.college_name = college_name
        profile_obj.branch = branch
        profile_obj.year = year
        profile_obj.save()
        messages.success(request, "Profile updated successfully")
        return redirect("/profile/?username=" + str(user_obj.username))


@login_required(login_url="/login")
def change_safe_mode(request):
    if request.method == "POST":
        user_obj = request.user
        user_id = user_obj.id
        profile_obj = Profile.objects.filter(user_id=user_id).first()

        if profile_obj.safe_mode:
            profile_obj.safe_mode = False
            profile_obj.save()
            messages.warning(request, "Safe mode disabled")
        else:
            profile_obj.safe_mode = True
            profile_obj.save()
            messages.success(request, "Safe mode enabled")
        # safe_mode = request.POST["safe_mode"]
        # profile_obj.safe_mode = safe_mode
        # profile_obj.save()
        # messages.success(request, "Safe Mode updated successfully")
        return redirect("/profile/?username=" + str(user_obj.username))


@login_required(login_url="/login")
def change_password(request):
    if request.method == "POST":
        old_password = request.POST["old_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        user = request.user
        if user.check_password(old_password):
            if new_password == confirm_password:
                if len(new_password) < 5:
                    messages.error(request, "Password is too short")
                    return redirect("/profile/?username=" + str(user.username))
                user.set_password(new_password)
                user.save()
                password_notification_email(user)
                messages.success(request, "Password changed successfully")
            else:
                messages.error(request, "Password did not match")
        else:
            messages.error(request, "Wrong password")
        return redirect("/logout")


@login_required(login_url="/login")
def change_profile_pic(request):
    if request.method == "POST":
        user_obj = request.user
        user_id = user_obj.id
        profile_obj = Profile.objects.filter(user_id=user_id).first()
        prev_profile_pic = profile_obj.profile_pic
        profile_pic = request.FILES["profile_pic"]
        file_name = profile_pic.name
        file_extension = file_name.split(".")[-1]
        if file_extension.lower() not in ["jpg", "jpeg", "png"]:
            messages.error(request, "Invalid file type")
            return redirect("/profile/?username=" + str(user_obj.username))
        else:
            profile_pic.name = str(user_obj.username) + "." + file_extension
        profile_obj.profile_pic = profile_pic
        profile_obj.save()
        if prev_profile_pic:
            os.remove(prev_profile_pic.path)
        messages.success(request, "Profile pic updated successfully")
        return redirect("/profile/?username=" + str(user_obj.username))


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["emailid"]
        username = request.POST["forgotusername"]
        if User.objects.filter(email=email).exists():
            user = User.objects.filter(email=email).first()
            if user.username == username:
                auth_token = str(uuid.uuid4())
                profile_obj = Profile.objects.filter(user_id=user.id).first()
                profile_obj.auth_token = auth_token
                profile_obj.save()
                send_forgotpass_mail(user, email, auth_token)
                messages.success(request, "Check your email for reset password link")
                return redirect("/login")
            else:
                messages.error(request, "Invalid username")
                return redirect("/forgotpassword")
        else:
            messages.error(request, "Email not found")
            return redirect("/forgot_password")
    return render(request, "Account/forgot_password.html")


def password_notification_email(user):
    profile = Profile.objects.filter(user_id=user.id).first()
    subject = "Password Changed Successfully"
    message = f"Hello {profile.fname}, \n\t This is a confirmation that your password for your Gurukul account {user.username} has just been changed.\nIf you didn't change your password, you can secure you account from here.\n\n{settings.BASE_URL}/forgot_password/\n\nSincerely\nTeam Gurukul"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)


def send_forgotpass_mail(user, email, auth_token):
    profile = Profile.objects.filter(user_id=user.id).first()
    subject = "Change Password for Gurukul"
    message = f"Hello {profile.fname}, \n\t Someone (hopefully you!) has requested to change your Gurukul password. Please click on the link below to change your password. \n\n{settings.BASE_URL}/reset_password/{auth_token} \n\nIf you did not request this, please ignore this email and your password will remain unchanged. \n\nSincerely\nTeam Gurukul"
    from_email = settings.EMAIL_HOST_USER
    to_list = [email]
    send_mail(subject, message, from_email, to_list, fail_silently=False)


def reset_password(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        if profile_obj:
            messages.success(request, "Autherized to reset password")
            return render(
                request, "Account/reset_password.html", {"auth_token": auth_token}
            )
        else:
            messages.error(request, "Invalid auth token")
            return redirect("/error")
    except Exception as e:
        print(e)
        messages.success(request, "Something went wrong")


def reset_password_submit(request, auth_token):
    if request.method == "POST":
        new_password = request.POST["newpassword"]
        confirm_password = request.POST["confirmpassword"]
        if new_password == confirm_password:
            if len(new_password) < 5:
                messages.error(request, "Password is too short")
                return redirect("/reset_password/" + auth_token)
            profile_obj = Profile.objects.filter(auth_token=auth_token).first()
            user = profile_obj.user
            user.set_password(new_password)
            user.save()
            password_notification_email(user)
            profile_obj.auth_token = ""
            profile_obj.save()
            messages.success(request, "Password changed successfully")

            return redirect("/login")
        else:
            messages.error(request, "Password did not match")
            return redirect("/reset_password/" + auth_token)
    messages.error(request, "Something went wrong")


###### Matplotlib

import matplotlib
matplotlib.use('Agg')  # Set to non-interactive backend

import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render

def plot_branch_distribution():
    # Get branch counts from the Profile model
    branch_counts = Profile.objects.values('branch').annotate(count=models.Count('branch'))

    # Prepare data for the pie chart
    branches = [item['branch'] for item in branch_counts]
    counts = [item['count'] for item in branch_counts]

    # Create a pie chart
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts, labels=branches, autopct='%1.1f%%', startangle=90, colors=['blue', 'green', 'red', 'orange', 'purple'])
    ax.set_title('Percentage of Students Registered by Branch')

    # Save the plot to a BytesIO object and encode it as a base64 string
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_str = base64.b64encode(img_buf.getvalue()).decode('utf-8')

    return img_str

def info(request):
    # Generate the pie chart image
    plot_image = plot_branch_distribution()

    # Render the info page with the pie chart
    return render(request, 'Account/info.html', {'plot_image': plot_image})
