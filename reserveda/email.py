from flask_mail import Message
from reserveda import app, mail
from flask import render_template
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, recipient, text_body, html_body):
    msg = Message(
        subject,
        sender=app.config["MAIL_USERNAME"],
        recipients=[recipient],
    )
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        "[Reserveda] Reset Your Password",
        recipient=user.email,
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
    )


def send_off_waitlist_email(user, item):
    send_email(
        f"[Reserveda] You've reserved {item.name}!",
        recipient=user.email,
        text_body=render_template("email/off_waitlist.txt", user=user, item=item),
        html_body=render_template("email/off_waitlist.html", user=user, item=item),
    )
