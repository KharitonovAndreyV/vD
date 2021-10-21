from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.forms import ResetPasswordRequestForm, ResetPasswordForm
import os
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email
from tkinter import *
import tkinter.filedialog as fd
from flask import jsonify
import imghdr
from flask import abort,send_from_directory
from werkzeug.utils import secure_filename

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required# декоратор не дает смотреть эту страницу(/index)
def index():
    form=PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Пост добавлен!')
        #обновляем страницу...
        return redirect(url_for('index'))
    title = {'title1':'Главная','title2':'Мой блог'}
    page=request.args.get('page',1,type=int)
    posts=current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url =url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url =url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=title, posts=posts.items,
        form=form, next_url=next_url, prev_url=prev_url)

@app.route('/explore')
@login_required# декоратор не дает смотреть эту страницу(/index)
def explore():
    title = {'title1':'Обзор'}
    page=request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    #posts=Post.query.order_by(Post.timestamp.desc()).all()
    next_url =url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url =url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=title, posts=posts.items,
        next_url=next_url, prev_url=prev_url)

@app.route('/user/<username>')
@login_required
def user(username):
    user=User.query.filter_by(username=username).first_or_404()
    page=request.args.get('page',1,type=int)
    posts=user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url =url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url =url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    #posts=[{'author':user, 'body':'test 1'},{'author':user, 'body':'test 2'}]
    return render_template('user.html', title='Профиль', user=user,
        posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/qwe')
@login_required# декоратор не дает смотреть эту страницу(/qwe)
def qwe():
    title = {'title1':'Обзор'}
    page=request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE_MAX'], False)
    #posts=Post.query.order_by(Post.timestamp.desc()).all()
    next_url =url_for('qwe', page=posts.next_num) \
        if posts.has_next else None
    prev_url =url_for('qwe', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('qwe.html', title=title, posts=posts.items,
        next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Не правильный логин или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')#выясняем куда перенаправлять после авторизации
        if not next_page or url_parse(next_page).netloc !='':#если некуда то на index
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('{}, Вы успешно зарегестрировались'.format(form.username.data))
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form=EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Сохранено')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Правка', form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('пользователь {} не найден.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Вы не можете подписаться на самого себя')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Вы подписались на {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('пользователь {} не найден.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Вы не можете подписаться на самого себя')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Вы подписались на {}.'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('На почту отправленно сообщение с инструкциями для сброса пароля')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Сброс пароля',
        form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль изменен.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.username =='pes':# захардкодил АДМИНКУ )))))
        print(current_user)
        return render_template('admin.html')
    else:
        return redirect(url_for('index'))

#Вызов ФЛАСК ВЬЮХИ из АЯКСА. жмешь кнопку на страничке, вызываешь эту функцию...
@app.route('/background_process_test')
def background_process_test():
    #print(fd.askopenfilename(title="открыть", initialdir="/"))
    #fileway=fd.askopenfile()
    #print(fileway.name)
    ddata = {"firs":"name","second":"xyename"}
    return ddata

#хрень для загрузки файлов---------------------------------------------------
#def validate_image(stream):#проверка, что фаил действительно картинка.
#    header = stream.read(512)
#    stream.seek(0)
#    format = imghdr.what(None, header)
#    if not format:
#        return None
#    return '.' + (format if format != 'jpeg' else 'jpg')

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/upload')
def uploaddd():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('upload.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    print(request.files['file'])
    print(uploaded_file.filename)
    print(filename)# не понимает русские файлы(((
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        #if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
        #        file_ext != validate_image(uploaded_file.stream):
        #    return "Invalid image", 400
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return '', 204

@app.route('/uploads/<filename>')
def uploads(filename):
    print(filename)
    print(app.config['UPLOAD_PATH2'])
    print(send_from_directory(app.config['UPLOAD_PATH2'], filename))
    return send_from_directory(app.config['UPLOAD_PATH2'], filename)
