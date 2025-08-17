from django.http.response import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UploadFiles
from datetime import datetime

# Create your views here.
@login_required(login_url="/login")
def Upload(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        ISBN = request.POST.get("ISBN")
        isBook = request.POST.get("isBook") == "on"  # Checkbox status
        bookfile = request.FILES.get("bookfile")

        # Basic validation
        if not title or not author or not bookfile:
            messages.error(request, "Title, author, and file are required.")
            return redirect("/library/upload")

        # Validate the file type
        filename = bookfile.name
        fileextention = filename.split(".")[-1].lower()
        if fileextention != "pdf":
            messages.error(request, "Only PDF files are allowed.")
            return redirect("/library/upload")

        # Rename the file
        name = (
            str(title.replace(" ", "_"))
            + str(datetime.now().strftime("%Y%m%d%H%M%S"))
            + "."
            + fileextention
        )
        bookfile.name = name

        # Handle image URL if it's a book
        image_url = None
        if isBook:
            if not ISBN:
                messages.error(request, "ISBN is required for books.")
                return redirect("/library/upload")
            image_url = f"https://covers.openlibrary.org/b/isbn/{ISBN}-L.jpg"

        # Save the file to the database
        try:
            UploadFiles.objects.create(
                title=title,
                author=author,
                ISBN=ISBN if isBook else None,
                isBook=isBook,
                bookfile=bookfile,
                image_url=image_url,
                timestamp=datetime.now(),
                uploadedby=request.user,
            )
            messages.success(request, "File uploaded successfully.")
        except Exception as e:
            messages.error(request, f"Something went wrong: {e}")

        return redirect("/library/upload")
    else:
        return render(request, "Library/uploadfiles.html")

@login_required(login_url="/login")
def feed(request):
    books = UploadFiles.objects.all()
    context = {"books": books}
    return render(request, "Library/feed.html", context)

@login_required(login_url="/login")
def delete_upload(request, serial_no):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to delete an upload.")
        return redirect('/login')

    # Get the book by serial_no
    book = get_object_or_404(UploadFiles, serial_no=serial_no)

    # Check if the current user is the one who uploaded the file
    if book.uploadedby == request.user:
        # Delete the file from the database
        book.delete()
        messages.success(request, "File deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this file.")

    return redirect('/library')  # Redirect back to the feed page