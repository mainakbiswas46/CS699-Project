from django.http.response import HttpResponse
from django.shortcuts import redirect, render

from Account.views import user
from .models import Question, Answer
from django.contrib import messages
from .templatetags import get_dict
from django.contrib.auth.decorators import login_required
from .models import Question, Answer
from django.contrib.auth.models import User
from datetime import datetime
from slugify import slugify
from Account.models import Profile

from better_profanity import profanity

# Create your views here.
@login_required(login_url="/login")
def feed(request):
    allposts = (
        Question.objects.all()
    )  # .objects --> Get all the objects from the database
    # print(allposts)
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

    context = {"allposts": allposts, "subjects": subjects}
    return render(request, "Question/feed.html", context)


@login_required(login_url="/login")
def question(request, slug):
    post = Question.objects.filter(slug=slug).first()  # .filter --> Filter the objects
    user = request.user
    if user.username != post.author:
        post.views = post.views + 1
        post.save()
    user_id = user.id
    profile = Profile.objects.filter(user_id=user_id).first()
    if profile.safe_mode:
        profanity.load_censor_words()
        post.title = profanity.censor(post.title)
        post.content = profanity.censor(post.content)
        post.tags = profanity.censor(post.tags)
    # Comments Corresponding to post
    comments = Answer.objects.filter(
        post=post, parent=None
    )  # .objects --> Get all the objects from the database
    replies = Answer.objects.filter(post=post).exclude(
        parent=None
    )  # .objects --> Get all the objects from the database
    # print(post)
    # print(comments, replies)
    reply_count = {}
    for comment in comments:
        if profile.safe_mode:
            profanity.load_censor_words()
            comment.comment = profanity.censor(comment.comment)

        reply_count[comment.serial_no] = Answer.objects.filter(parent=comment).count()

    # Key = Comment_Id (Serial_No) & Value = List of Replies (whose parent is the comment.serial_no)
    reply_Dict = {}
    for reply in replies:
        if profile.safe_mode:
            profanity.load_censor_words()
            reply.comment = profanity.censor(reply.comment)
        # Initial
        if reply.parent.serial_no not in reply_Dict.keys():
            reply_Dict[reply.parent.serial_no] = [reply]
        # Append
        else:
            reply_Dict[reply.parent.serial_no].append(reply)

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

    if post.likes.filter(id=user.id).exists():
        liked = True
    else:
        liked = False

    if post.dislikes.filter(id=user.id).exists():
        disliked = True
    else:
        disliked = False

    context = {
        "post": post,
        "comments": comments,
        "user": request.user,
        "reply_Dict": reply_Dict,
        "reply_count": reply_count,
        "subjects": subjects,
        "liked": liked,
        "disliked": disliked,
    }
    return render(request, "Question/question.html", context)
    # return HttpResponse(f'Blog Post : {slug}')


@login_required(login_url="/login")
def comment(request):
    # profanity.load_censor_words()

    if request.method == "POST":
        comment = request.POST.get("comment")
        user = request.user

        post_serial_no = request.POST.get("post_serial_no")
        parent_serial_no = request.POST.get("parent_serial_no")

        post = Question.objects.filter(serial_no=post_serial_no).first()

        # comment = profanity.censor(comment)

        if parent_serial_no == "":
            comment = Answer(comment=comment, user=user, post=post)
            comment.save()
            post.total_answers = post.total_answers + 1
            post.save()
            messages.success(request, "Your comment has been posted successfully.")

        else:
            parent = Answer.objects.get(serial_no=parent_serial_no)
            comment = Answer(comment=comment, user=user, post=post, parent=parent)
            comment.save()
            messages.success(request, "Your reply has been posted successfully.")

    return redirect(f"/question/{post.slug}")


@login_required(login_url="/login")
def uploadquestion(request):
    # profanity.load_censor_words()

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        subject = request.POST.get("subject")
        author = request.user
        tags = request.POST.get("tags")
        user = request.user
        profile = Profile.objects.filter(user=user).first()
        branch = profile.branch
        # title = profanity.censor(title)
        # content = profanity.censor(content)

        temp = slugify(title, to_lower=True, separator="-", max_length=90)
        slug = str(author.id) + "-" + str(temp)
        timestamp = datetime.now()
        if Question.objects.filter(slug=slug).exists():
            slug = slug + "-" + str(timestamp)
            slug = slugify(slug, to_lower=True, separator="-", max_length=90)

        if title and content and author and slug and subject:
            try:
                Question.objects.create(
                    title=title,
                    content=content,
                    subject=subject,
                    author=author,
                    slug=slug,
                    timestamp=timestamp,
                    tags=tags,
                    branch=branch,
                )
                messages.success(request, "Question uploaded successfully")

            except:
                messages.error(request, "Something went wrong")
        return redirect("/question")


@login_required(login_url="/login")
def filter(request):
    query = request.GET["subject"]
    allposts = Question.objects.filter(subject__icontains=query)
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
    context = {"allposts": allposts, "subjects": subjects}
    return render(request, "Question/feed.html", context)
    # return HttpResponse('Search')


@login_required(login_url="/login")
def edit_question(request):
    # profanity.load_censor_words()

    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        subject = request.POST["subject"]
        slug = request.POST["slug"]
        post = Question.objects.get(slug=slug)

        # title = profanity.censor(title)
        # content = profanity.censor(content)

        if title == "":
            title = post.title
        if content == "":
            content = post.content
        if subject == "":
            subject = post.subject
        if title and content and content and slug and subject:
            try:
                post.title = title
                post.content = content
                post.subject = subject
                post.edited_timestamp = datetime.now()
                post.edited = True
                post.save()
                messages.success(request, "Question edited successfully")

            except:
                messages.error(request, "Something went wrong")
        return redirect("/question/" + str(slug))


@login_required(login_url="/login")
def delete_question(request):
    if request.method == "POST":
        slug = request.POST["slug"]
        post = Question.objects.get(slug=slug)
        post.delete()
        messages.success(request, "Question deleted successfully")
        return redirect("/question")


@login_required(login_url="/login")
def edit_answer(request):
    # profanity.load_censor_words()

    if request.method == "POST":
        comment = request.POST["comment"]
        post_serial_no = request.POST["post_serial_no"]
        comment_serial_no = request.POST["comment_serial_no"]

        answer = Answer.objects.get(serial_no=comment_serial_no)
        post = Question.objects.get(serial_no=post_serial_no)

        # comment = profanity.censor(comment)

        if comment == "":
            comment = answer.comment

        if comment and post and comment_serial_no:
            try:
                answer.comment = comment
                answer.edited_timestamp = datetime.now()
                answer.edited = True
                answer.save()
                messages.success(request, "Answer edited successfully")
            except:
                messages.error(request, "Something went wrong")
        return redirect(f"/question/{post.slug}")


@login_required(login_url="/login")
def delete_answer(request):
    if request.method == "POST":
        comment_serial_no = request.POST["comment_serial_no"]
        post_serial_no = request.POST["post_serial_no"]
        post = Question.objects.get(serial_no=post_serial_no)
        answer = Answer.objects.get(serial_no=comment_serial_no)
        answer.delete()
        messages.success(request, "Answer deleted successfully")
        return redirect(f"/question/{post.slug}")


@login_required(login_url="/login")
def edit_reply(request):
    # profanity.load_censor_words()

    if request.method == "POST":
        comment = request.POST["reply"]
        slug = request.POST["slug"]
        # post_serial_no = request.POST["post_serial_no"]
        comment_serial_no = request.POST["comment_serial_no"]

        reply = Answer.objects.get(serial_no=comment_serial_no)

        # comment = profanity.censor(comment)

        if comment == "":
            comment = reply.comment

        if comment and comment_serial_no:
            try:
                reply.comment = comment
                reply.edited_timestamp = datetime.now()
                reply.edited = True
                reply.save()
                messages.success(request, "Reply edited successfully")
            except:
                messages.error(request, "Something went wrong")
        return redirect(f"/question/{slug}")


@login_required(login_url="/login")
def delete_reply(request):
    if request.method == "POST":
        comment_serial_no = request.POST["comment_serial_no"]
        slug = request.POST["slug"]
        reply = Answer.objects.get(serial_no=comment_serial_no)
        reply.delete()
        messages.success(request, "Reply deleted successfully")
        return redirect(f"/question/{slug}")


@login_required(login_url="/login")
def like_question(request):
    if request.method == "POST":
        slug = request.POST["post_id1"]
        post = Question.objects.get(slug=slug)
        user = request.user
        if post.dislikes.filter(id=user.id).exists():
            post.dislikes.remove(user)
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
        else:
            post.likes.add(user)
        post.save()
        user = request.user
        return redirect(f"/question/{slug}")


@login_required(login_url="/login")
def dislike_question(request):
    if request.method == "POST":
        slug = request.POST["post_id2"]
        post = Question.objects.get(slug=slug)
        user = request.user
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
        if post.dislikes.filter(id=user.id).exists():
            post.dislikes.remove(user)
        else:
            post.dislikes.add(user)
        post.save()
        user = request.user
        return redirect(f"/question/{slug}")


@login_required(login_url="/login")
def sort_feed(request):
    if request.method == "GET":
        sort = request.GET["sort"]

        allposts = (
            Question.objects.all()
        )  # .objects --> Get all the objects from the database
    # print(allposts)
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

    if sort == "newest":
        allposts = allposts.order_by("-timestamp")
        sortedby = "Newest"
    elif sort == "oldest":
        allposts = allposts.order_by("timestamp")
        sortedby = "Oldest"
    elif sort == "mostlikes":
        allposts = allposts.order_by("-likes")
        sortedby = "MostLikes"
    elif sort == "minlikes":
        allposts = allposts.order_by("likes")
        sortedby = "MinLikes"
    elif sort == "mostdislikes":
        allposts = allposts.order_by("-dislikes")
        sortedby = "MostDislikes"
    elif sort == "mindislikes":
        allposts = allposts.order_by("dislikes")
        sortedby = "MinDislikes"
    elif sort == "mostviews":
        allposts = allposts.order_by("-views")
        sortedby = "MostViews"
    elif sort == "minviews":
        allposts = allposts.order_by("views")
        sortedby = "MinViews"
    elif sort == "mostanswers":
        allposts = allposts.order_by("-total_answers")
        sortedby = "MostAnswers"
    elif sort == "minanswers":
        allposts = allposts.order_by("total_answers")
        sortedby = "MinAnswers"

    # allposts = allposts.order_by("-timestamp")
    if profile.safe_mode:
        for post in allposts:
            profanity.load_censor_words()
            post.title = profanity.censor(post.title)
            post.content = profanity.censor(post.content)
            post.tags = profanity.censor(post.tags)

    context = {"allposts": allposts, "subjects": subjects, "sortedby": sortedby}
    return render(request, "Question/feed.html", context)
