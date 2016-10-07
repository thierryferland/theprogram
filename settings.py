import os
import sys
from google.appengine.ext import vendor
import datetime

GOOGLE_SECRET = ''
TOKEN_SECRET = ''
WEB_CLIENT_ID = ''
ANDROID_CLIENT_ID = ''
IOS_CLIENT_ID = ''
DEBUG = False

CUTOFF_DATE = datetime.datetime(2016,10,01,0,0,0)

sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))
vendor.add('server/lib')