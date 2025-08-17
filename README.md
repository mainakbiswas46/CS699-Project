## <!-- ABOUT THE PROJECT -->

## About The Project:

This platform was created as part of our Software Lab Project with the aim of supporting GATE aspirants during their preparation journey. Our goal is to provide a space for students to share their question-answer sets, upload solutions with markdown support (so your algorithm's pseudocode doesn't look messy), and keep motivated through a profanity filter, ensuring that no negative language hinders your focus.

---

### Team Members
- ARITRA BELEL (24M0814)
- HIRENMAY SAMANTA (24M0794)
- MAINAK BISWAS (24M0816)

---

### Installation:

- To install `Django` and other dependencies on your machine run this command.

```
pip install -r requirements.txt
```

### Environment Setup

Before Starting the Server

1. Create `.env` file inside root project directory.
2. Add `EMAIL` , `PASSWORD` and `SECRET_KEY` variables into `.env` file.

```
echo "EMAIL = \nPASSWORD = \nSECRET_KEY = " > .env
```

3. Give propper values to the variables & for `Password` enter the login password of your email.

> For `PASSWORD` :
>
> - Copy [`app passwords`](https://myaccount.google.com/u/0/apppasswords) and paste in  <b>.env</b> file.

> For `SECRET_KEY` :
>
> - Copy & run the following command in terminal.
>
> ```ruby
> django-admin startproject myproject
> cd myproject/myproject
> ```
>
> - Now open `settings.py` file and copy the `SECRET_KEY` value from line number `23`.
>
> ( Sample `SECRET_KEY` : `django-insecure-&)#p8aqf*r0pxv_ui2lxhxgax&@psu1@+jk9gi^vq3af0gqixi` )

### Make Migration and Migrate:

```ruby
python manage.py makemigrations
python manage.py migrate
```

### Run the server :

```ruby
python manage.py runserver
```

Now you can access the server at <a href="http://localhost:8000/">`http://localhost:8000/`</a>.

---

## Features:

- [Account](./Account):

  - Login & Signup
  - Email Verification
  - Forgot Password
  - Update Profile Picture
  - Edit Profile & Change Password
  - 3 time login attempts
  - Safe Mode

- [Question](./Question):

  - Ask Question
  - Answer Question
  - Like & Dislike
  - Edit & Delete Question/Answer
  - Realtime Views count
  - Search Question
  - Filter Questions according to the tags
  - Sort Questions on the basis of time/views/likes/answers
  - Markdown Support
  - Profanity Filter (Forbidden words will be replaced with `*`, if safe mode is on)

- [Library](./Library):
  - Add Books/Notes
  - Preview Books/Notes
  - Download Books/Notes
  - Delete Books/Notes (Only for Uploader)

---