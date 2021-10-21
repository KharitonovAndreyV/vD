import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
#переменные для отправки почты
#    MAIL_SERVER=smtp.googlemail.com
#    MAIL_PORT=587
#    MAIL_USE_TLS=1
#    MAIL_USERNAME=erohinak676
#    MAIL_PASSWORD=Thj[byf3648
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS=['hariton_1@bk.ru']#адресс

    LANGUAGES = ['en','ru']
    POSTS_PER_PAGE = 6
    POSTS_PER_PAGE_MAX = 100
#для загрузки файлов
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    UPLOAD_EXTENSIONS = ['.docx', '.doc', '.png', '.gif']
    #UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
    UPLOAD_PATH = 'app\static'
    UPLOAD_PATH2 = 'static'
    #UPLOAD_PATH = 'd:\py\vD\uploads2'
