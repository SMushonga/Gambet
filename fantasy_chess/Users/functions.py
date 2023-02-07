from flask import url_for, current_app, render_template
from flask_mail import Message
from fantasy_chess import mail


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Gambet Password Reset', sender='shingaim@chessgambet.com', recipients=[user.email])
    msg.body = f'''To reset your Gambet password, visit the following link:
        {url_for('users.reset_token', token=token, _external=True)}
        If you did not make this request then simply ignore this email and no changes will be made.
        '''
    mail.send(msg)

#Need a better support/query management system than just sending an email from ourselves to our address
def send_query_email(email, message, category):
    msg = Message(
        f'Query from {email}',
        sender='shingaim@chessgambet.com', 
        recipients=['shingaim@chessgambet.com'],
        html=render_template('email_templates/query_email.html', category=category, message=message))
    mail.send(msg)
