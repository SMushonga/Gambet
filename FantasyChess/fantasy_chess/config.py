import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    STRIPE_SECRET_KEY = 'sk_test_51MEvEEBnteUfgja4okpLxfjYGH9I6Z00vla9P7PLBF0Tf9SppzyzL8Akg3I16dRK0Lq5otLJIiKVxwz1WqkyxOUf004xNnkvsA'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')