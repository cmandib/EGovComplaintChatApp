# EGov Complaint Chat App

A web app where someone with evidence that labour laws are being broken can sign up and chat directly with a labour inspector, send them files, and keep the whole conversation in one place, instead of going to an office in person.

We built it for the E-Governance lab in the B.Sc. CSIT program at Samriddhi College, between February and April 2025. The scenario was the Ministry of Labour, Employment and Social Security (MoLESS) in Nepal. It's a student project, not a system the ministry runs.

Team: Mandib Chaulagain, Jonathan Rana Magar, Mirack Hang Subba.

## What it does

- Sign up and log in with your email (django-allauth). After signing up you land on a profile page to add a display name, a photo and a short bio.
- Citizens get a **My Inspectors** page that lists every inspector. Clicking one opens a private chat. If you already have a chat with that inspector, it takes you back to it instead of opening a new one.
- Inspectors get a **Complainers** page listing everyone who has started a chat with them.
- Messages appear on both sides right away over a websocket, with no page refresh.
- You can attach files (photos, documents, whatever the evidence is) to the chat.
- The chat header shows whether the other person is online.
- Profile settings let you change your email (it sends a new confirmation), resend the verification email, or delete your account.

Inspectors are just Django superusers. There's no separate role, so every superuser shows up in the inspector list.

## How it's put together

Django with Django Channels for the websockets, served by Daphne. The front end is server-rendered templates with HTMX and its websocket extension, Alpine.js for the profile dropdown, hyperscript to clear the input after sending, and Tailwind from the CDN. There's no JavaScript build step.

What happens when you send a message:

1. The message form in `chat.html` connects to `/ws/chatroom/<room name>` through `hx-ext="ws"`.
2. `ChatroomConsumer.receive` in `a_rtchat/consumers.py` saves a `GroupMessage` and broadcasts its id to everyone in that room's channel group.
3. Each connected consumer renders `partials/chat_message_p.html` and sends the HTML down the socket. The partial uses `hx-swap-oob`, so HTMX appends it to the message list.

File uploads are a normal HTMX POST to `chat_file_upload`. It saves the file and sends the same broadcast event, so the other person sees it come in too. Online status works the same way: on connect and disconnect the consumer updates `ChatGroup.users_online` and pushes a fresh `online_count.html` partial.

```
realtime_chat/      the app itself
  a_core/           settings, urls, asgi.py (http + websocket routing)
  a_home/           home page and the inspector / complainer list
  a_users/          Profile model, signals, profile and settings pages
  a_rtchat/         ChatGroup and GroupMessage models, consumer, chat views and templates
  templates/        base layout, header, allauth overrides
  static/           css and images
htmx_demo/          a separate little Django project we used to try out HTMX
                    (a user list that polls every 2 seconds); not part of the app
```

## Running it locally

```bash
cd realtime_chat
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
pip install "django-allauth==65.7.0" "Django==5.2.*"
```

The second `pip install` matters. `requirements.txt` isn't pinned, and newer django-allauth releases removed `send_email_confirmation`, which `a_users/views.py` imports, so the app won't start on the latest version. Last checked with Python 3.14, Django 5.2.18 and django-allauth 65.7.0.

Migrations are in `.gitignore`, so create them first:

```bash
python manage.py makemigrations a_users a_rtchat
python manage.py migrate
python manage.py createsuperuser     # this account is your first inspector
python manage.py runserver
```

Because `daphne` is first in `INSTALLED_APPS`, `runserver` starts the ASGI server and websockets work with nothing else to set up.

Open http://127.0.0.1:8000 and log in as the superuser. In a private window, sign up as a normal user, open **My Inspectors** and start a chat. Emails (signup confirmation, email change) are printed in the terminal, because `EMAIL_BACKEND` is the console backend.

`/mainchat/` is meant to be a public room. It only works if a `ChatGroup` called `public-chat` exists, which you can create from `/admin`. Without it, the page returns a 404.
