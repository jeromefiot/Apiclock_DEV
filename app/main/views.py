# coding: utf-8
import os

from flask import render_template, redirect, url_for, flash, request,\
                  current_app, g
from flask.ext.login import login_user, login_required, current_user

from . import main
from .forms import EditProfileForm, EditProfileAdminForm, playerForm,\
                   ContactForm, snoozeForm, ChronoForm, LoginForm
from .. import db
from ..my_mpd import PersistentMPDClient
from ..email import send_email
from ..models import Role, User, Alarm, Music
from ..decorators import admin_required
from ..login_nav import LoginFormNav
from ..functions import snooze, Chrono


# mpd_player = player()
mpd_player = PersistentMPDClient()

# ========================================
# ============= PUBLIC PAGES  ============
# ========================================


@main.before_request
def mpd_status():
    if current_user.is_authenticated():
        mpd_status = mpd_player.is_playing()
        print mpd_status


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or
                            url_for('.dashboard'))
            # return redirect(url_for('.dashboard'))
        flash('Invalid username or password.')
        return redirect(url_for('.login'))
    return render_template('src/API_signin.html', form=form)


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)

    form2 = LoginFormNav()
    form2.validateFormNav()

    # if request.method == 'POST':
    #
    #     if form.validate() == False:
    #         flash('All fields are required.')
    #         return render_template('src/SITE_contact.html', form=form)
    #     else:
    #     msg = Message(form.data['subject'],
    #                   sender='[Contact] - Apiclock',
    #                   recipients=['j_fiot@hotmail.com'])
    #     msg.body = """
    #     From: %s &lt; %s &gt; %s """ % (form.data['name'],
    #                                     form.data['email'],
    #                                     form.data['message'])
    #     send_email('j_fiot@hotmail.com',
    #                'APICLOCK MAIL from ' + form.data['email'],
    #                'auth/email/contact',
    #                msg.body)

    if request.method == 'POST':
        user_name = form.data['name']
        user_mail = form.data['email']
        subject = form.data['subject']
        message = form.data['message']

        send_email('jeromefiot@gmail.com',
                   'Contact APICLOCK',
                   'auth/email/contact',
                   name=user_name,
                   mail=user_mail,
                   message=message,
                   subject2=subject)
        flash('An email has been sent to Jerome. \
               He will answer as soon as possible. Have a nice day !')
        return render_template('src/SITE_contact.html', success=True)

    elif request.method == 'GET':
        # return render_template('public/contact.html', form=form, form2=form2)
        return render_template('src/SITE_contact.html', form=form)


@main.route('/apiclock')
def apiclock():
    return render_template('src/SITE_home.html')
    # return render_template('index.html')


@main.route('/presentation')
def presentation():
    # return render_template('src/presentation.html')
    return render_template('src/API_blog.html')


@main.route('/installation')
def installation():
    form2 = LoginFormNav()
    form2.validateFormNav()
    return render_template('public/installation.html', form2=form2)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/', methods=['GET', 'POST'])
def index():
    """Index."""
    form2 = LoginFormNav()
    if form2.validateFormNav():
        form1 = playerForm(prefix="form1")
        formsnooze = snoozeForm()
        form_chrono = ChronoForm()
        return render_template('dashboard.html',
                               form1=form1,
                               formsnooze=formsnooze,
                               form_chrono=form_chrono)
    else:
        return render_template('index.html', form2=form2)

# ========================================
# ============= PRIVATE PAGES ============
# ========================================


@main.route('/dashboard', methods=['GET', 'POST'], defaults={'action': 4})
@main.route('/dashboard/<action>/<musique>', methods=['GET', 'POST'])
@login_required
@admin_required
def dashboard(action,
      musique="http://audio.scdn.arkena.com/11010/franceculture-midfi128.mp3"):

    """Get and Print MPD state."""
    MPDstatut = mpd_player.is_playing()
    # MPDstatut = None

    alarms = Alarm.query.filter_by(users=current_user.id).all()
    form1 = playerForm(prefix="form1")
    # formsnooze = snoozeForm()
    # form_chrono = ChronoForm(prefix="form_chrono")

    # if formsnooze.submitsnooze.data:
    #     """Get radio by id and return url."""
    #     radiosnooze = formsnooze.radiosnooze.data
    #     radiosnooze = Music.query.filter(Music.id == radiosnooze).first()
    #     radiosnooze = radiosnooze.url
    #     minutessnooze = int(formsnooze.minutessnooze.data)
    #     snooze(radiosnooze, minutessnooze)
    #     return redirect(url_for('.dashboard'))

    # elif form_chrono.submit.data:
    #     """CHRONO : Depending on media type, get id and then request for url"""
    #     delay_chrono = int(form_chrono.chrono_minutes.data)
    #
    #     if form_chrono.radio.data != "0":
    #         """
    #         launch chrono (func and thread) with radio url
    #         and choosen delay.
    #         """
    #         mediaid = form_chrono.radio.data
    #         choosen_media = Music.query.filter(Music.id == mediaid).first()
    #         Chrono(choosen_media.url, delay_chrono)
    #
    #     elif form_chrono.radio.data == "0" and form_chrono.music.data != "0":
    #         """launch chrono (func and thread) with music and choosen delay"""
    #         mediaid = form_chrono.music.data
    #         choosen_media = Music.query.filter(Music.id == mediaid).first()
    #         Chrono(choosen_media.url, delay_chrono)
    #
    #     elif form_chrono.radio.data == "0" and form_chrono.music.data == "0":
    #         """Check form validity : no missing values."""
    #         mediaid = "0"
    #         flash("No media selected, please select a radio or music !")
    #     else:
    #         flash("No media selected, please select a radio or music !")
    #     return redirect(url_for('.dashboard'))

    if form1.submit.data:
        """PLAY : Depending on media type, get id and then request for url."""

        if form1.radio.data != "0":
            mediaid = form1.radio.data
            choosen_media = Music.query.filter(Music.id == mediaid).first()
            mpd_player.play_media(choosen_media.url)

        elif form1.radio.data == "0" and form1.music.data != "0":
            mediaid = form1.music.data
            print mediaid
            choosen_media = Music.query.filter(Music.id == mediaid).first()
            mpd_player.play_media(choosen_media.name)

        elif form1.radio.data == "0" and form1.music.data == "0":
            mediaid = "0"
            flash("No media selected, please select a radio or music !")
        else:
            flash("No media selected, please select a radio or music !")

        return redirect(url_for('.dashboard'))

    # get in GET the action's param
    elif action == '1':
        """Play the urlmedia in args with volum."""
        mpd_player.play_media()
        return redirect(url_for('.dashboard'))

    elif action == '0':
        """Stop and clear MPD playlist."""
        mpd_player.stop()
        return redirect(url_for('.dashboard'))

    elif action == '2':
        """Increase volume."""
        mpd_player.volup()
        return redirect(url_for('.dashboard'))

    elif action == '3':
        """Decrease volume."""
        mpd_player.voldown()
        return redirect(url_for('.dashboard'))

    elif action == '4':
        """Display status"""
        mpd_player.next_play()
        return redirect(url_for('.dashboard'))

    else:
        return render_template('dashboard.html', form1=form1,
                            #    form_chrono=form_chrono,
                            #    formsnooze=formsnooze,
                               alarms=alarms,
                               )


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))

    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))

    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    user = User.query.all()
    if request.args.get('id'):
        userid = request.args.get('id')
        userd = User.query.filter(User.id == userid).first()
        db.session.delete(userd)
        db.session.commit()
        flash('The user has been deleted.')
        return redirect(url_for('.users', users=user))
    return render_template('admin/users.html', users=user)


@main.route('/config', methods=['GET', 'POST'])
@login_required
@admin_required
def config():
    app = current_app._get_current_object()
    # list config values containing FLASKY
    list_config = [[key, value] for key, value in app.config.iteritems()
                   if 'FLASKY' in key]

    return render_template('admin/config.html', config=list_config)
