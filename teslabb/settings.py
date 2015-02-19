# -*- coding: utf-8 -*-
"""
18.11.2013 19:24:23
muslu yüksektepe
"""

muslu = u"yüksektepe"

import os
import os.path
import re




BASE_DIR = os.path.dirname( os.path.dirname( __file__ ) )

Temp_Path = os.path.realpath( '.' )

SECRET_KEY = 'dwg77p@dvthfhfjtktmtum!rCEmMusluCeylany-Muslu'

DEBUG = False
TEMPLATE_DEBUG = True

COMPRESS_HTML = True

SEND_BROKEN_LINK_EMAILS = False

#
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = 'bilgi@spormarket.com.tr'
SERVER_EMAIL = 'bilgi@spormarket.com.tr'
EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.spormarket.com.tr'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'bilgi@spormarket.com.tr'
EMAIL_HOST_PASSWORD = 'BIlSM2015'

# DEFAULT_FROM_EMAIL      =       'sporthinkcomtr@gmail.com'
# SERVER_EMAIL            =       'sporthinkcomtr@gmail.com'
# EMAIL_USE_TLS           =       True
# EMAIL_HOST              =       'smtp.gmail.com'
# EMAIL_PORT              =       587
# EMAIL_HOST_USER         =       'sporthinkcomtr@gmail.com'
# EMAIL_HOST_PASSWORD     =       'GC9DustxxCYWK38'




IGNORABLE_404_URLS = (
re.compile( r'^/apple-touch-icon.*\.png$' ), re.compile( r'^/favicon\.ico$' ), re.compile( r'^/robots\.txt$' ),
)

ADMINS = (  # ('Muslu', 'musluyuksektepe@gmail.com'),
            ('Hata', 'hata@spormarket.com.tr'),
)

MANAGERS = ADMINS

LANGUAGE_CODE = 'tr_TR'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_L10N = True
USE_TZ = False
ALLOWED_HOSTS = ['www.spormarket.com.tr', 'spormarket.com.tr']



# URUN_RESIMLERI =  '/home/muslu/django/sporthink/media/urun_resimleri/'
MEDIA_ROOT = BASE_DIR + '/media/'
MEDIA_ROOT_ARSIV = BASE_DIR + '/arsiv/'

MEDIA_URL = '/media/'

STATIC_ROOT = BASE_DIR + "/static/"

STATIC_URL = '/static/'

TEMPLATE_DIRS = (
BASE_DIR + "/templates",
)

ADMIN_MEDIA_PREFIX = '/media/admin/'

TEMPLATE_LOADERS = (
('django.template.loaders.cached.Loader', (
'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader',
)),
)

TEMPLATE_CONTEXT_PROCESSORS = (  # "django.core.context_processors.csrf",
                                 "django.contrib.auth.context_processors.auth", "django.core.context_processors.debug", "django.core.context_processors.i18n", "django.core.context_processors.media", "django.core.context_processors.static", "django.core.context_processors.tz", "django.contrib.messages.context_processors.messages", "django.core.context_processors.request",
)

INSTALLED_APPS = (
'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'django.contrib.humanize', 'tinymce', 'suit', 'smart_selects',  # ~ 'grappelli',
'django.contrib.admin',

'kategoriler', 'kampanyalar', 'uyeler', 'siteayarlari', 'bankalar',  # 'permissivecsrf',
'django.contrib.sitemaps', 'suit_redactor', 'daterange_filter'  # ~ "compressor",

)




# CACHE_BACKEND = 'memcached://77.245.155.254:11211;127.0.0.1:11211/'

# CACHE_BACKEND = 'locmem:///'

# CACHES = {
# 'default': {
# 'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': '/var/tmp/django_cache',
#     }
# }

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': 'unix:/tmp/memcached.sock',
#     }
# }

STATICFILES_FINDERS = (
'django.contrib.staticfiles.finders.AppDirectoriesFinder', 'django.contrib.staticfiles.finders.FileSystemFinder',
)

MIDDLEWARE_CLASSES = (  # 'django.middleware.csrf.CsrfViewMiddleware',
                        'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'kategoriler.mobile.IPOgrenMiddleware', 'kategoriler.compress.MinifyHTMLMiddleware',
)

TINYMCE_JS_URL = 'http://www.spormarket.com.tr/static/tiny_mce/tiny_mce_src.js'
TINYMCE_DEFAULT_CONFIG = { 'plugins': "table,spellchecker,paste,searchreplace", 'theme': "advanced", 'cleanup_on_startup': True, 'custom_undo_redo_levels': 10, }
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = False

ISTENMEYENMARKALAR = ['CAT', 'CUBE', 'ENDER SPOR', 'FARELL', u'ÇÇS', u'LACOSTE', 'DOGUKAN', 'BOAONDA', u'BİGOS', 'GD', 'JAGHS', 'NORTHERN REBEL', 'PROTEST', 'REEF', 'VODEN', 'WIPEOUT', 'ZEUS', 'MOLTEN', 'BYOS', 'WILSON', 'NONE']


#USE_THOUSAND_SEPARATOR  =       True
#DECIMAL_SEPARATOR       =       ','
#THOUSAND_SEPARATOR      =       '.'
# NUMBER_GROUPING=3


YONLENDIRME = (
"/yonlendirmeler/" + ":15", "/yeniuyekampanya/" + ":15"
)

import logging




logging.basicConfig( level = logging.INFO, format = '%(asctime)s %(levelname)s %(message)s', filename = '/home/muslu/django/djangoLog.log', )

AUTHENTICATION_BACKENDS = (
'teslabb.backend.EmailAuthBackEnd', 'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'teslabb.urls'

WSGI_APPLICATION = 'teslabb.wsgi.application'


# PREPEND_WWW             =       True

DATABASES = { 'default': { 'NAME': 'SporMarketDB', 'ENGINE': 'django.db.backends.mysql', 'USER': 'DjangoUser', 'PASSWORD': 'Cem+35-+', 'HOST': 'localhost', 'PORT': '3306', },

              # 'default2': {
              #     'NAME': 'DjangoYedek',
              #     'ENGINE': 'django.db.backends.mysql',
              #     'USER': 'DjangoUser',
              #     'PASSWORD': 'muslu35',
              #     'HOST': 'localhost',
              #     'PORT': '3306',
              # },


              'V3': { 'ENGINE': 'django_pyodbc', 'NAME': 'V3_DOGUKAN', 'HOST': '88.250.159.71', 'USER': 'sa', 'PASSWORD': 'Gil_0150', 'PORT': 1436, 'OPTIONS': { 'driver': 'FreeTDS', 'host_is_server': True, 'dsn': 'sqlserver_V3', 'autocommit': True, 'extra_params': "TDS_VERSION=8.0; CHARSET=UTF8;" } },

}

SUIT_CONFIG = { 'ADMIN_NAME': 'Spormarket - Admin', 'HEADER_DATE_FORMAT': 'l, j. F Y',  # Saturday, 16th March 2013
                'HEADER_TIME_FORMAT': 'H:i',  # 18:42
                'CONFIRM_UNSAVED_CHANGES': True, 'LIST_PER_PAGE': 100

}

SITE_ADI = 'Spormarket'
DOMAIN = 'http://www.spormarket.com.tr'
FB_ADMIN = '000000000000'
FIYAT_ARALIGI = 20
KARGO_KAMPANYA = 100
KARGO_KAMPANYA_ARALIGI = 20
EN_AZ_SEPET_TUTARI = 5
EN_AZ_SEPET_TUTARI_KK = 100
KARGO_TUTARI = "6.90"
PUANHARCAMALIMITI = 30
NORMAL_STOK = 5
KRITIK_STOK = 2
FAZLA_STOK = 10
HIZMET_BEDELI = "7.50"
SMS_UCRETI = "0.15"
URUNADI_TEMIZLE = 2  # karakterden az olan açıklamaları temizler Örn: ERKEK PANTOLON UK SS --> ERKEK PANTOLON

SANTRAL_SABIT_IP = "88.250.159.71"
SANTRAL_IP = "192.168.2.101"
SANTRAL_DAHILI = "105"
SANTRAL_PORT = "5140"
SANTRAL_CLICK2CALL = "/Services/callservice.aspx?username=click2call&password=cl12sprtf&exten="



#
#



YENIUYELIK_MAILI = 'destek@spormarket.com.tr'
YENISIPARIS_MAILI = 'destek@spormarket.com.tr'

MARKAYA_AIT_URUNLERI_GOSTER = True
ALTKATEGORIYE_AIT_URUNLERI_GOSTER = True
FIYATI_BENZER_URUNLERI_GOSTER = True
ESLESTIRILMIS_KATEGORIURUNLERI_GOSTER = True
ESLESTIRILMIS_URUNLERI_GOSTER = True

SMS_ILE_ONAY = False

LOGIN_URL = '/uyegirisyap/'
LOGOUT_URL = '/uyecikisyap/'

FACEBOOK_APP_ID = '675280715866959'
FACEBOOK_APP_SECRET = 'a59ae9a6ef3959dfa400be4c95791dba'
FACEBOOK_SCOPE = 'email,publish_stream'




# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False
# SESSION_EXPIRE_AT_BROWSER_CLOSE=True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



OKURL_AKBANK = "http://spormarket.com.tr/odemeyapildi/"  # Islem basariliysa dönülecek isyeri sayfasi  (3D isleminin ve ödeme isleminin sonucu
FAILURL = "http://spormarket.com.tr/odemeyapilamadi/"  # Islem basarizsa dönülecek isyeri sayfasi  (3D isleminin ve ödeme isleminin sonucu)

COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT
