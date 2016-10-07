# -*- coding: latin-1 -*-

"""Epic Balance API
"""

import os
import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
import settings
from model import models
from google.appengine.ext import blobstore
import datetime
import jwt
from settings import CUTOFF_DATE, WEB_CLIENT_ID, ANDROID_CLIENT_ID, IOS_CLIENT_ID

ANDROID_AUDIENCE = WEB_CLIENT_ID

package = 'Balance'

class Date(messages.Message):
    day = messages.IntegerField(1)
    month = messages.IntegerField(2)
    year = messages.IntegerField(3)

class Message(messages.Message):
    message = messages.StringField(1)

class User(messages.Message):
    name = messages.StringField(1)
    email = messages.StringField(2)
    user_id = messages.StringField(3)
    
class Stats(messages.Message):
    n_drinks = messages.StringField(1)
    weekly_average = messages.StringField(2)
    sober_hours = messages.StringField(3)
    UI_hours = messages.StringField(4)
    UI_hours_per_week = messages.StringField(5)
    UI_percent = messages.StringField(6)
    owes = messages.StringField(7)
    points = messages.StringField(8)

class Token(messages.Message):
    token = messages.StringField(1)

class Drink(messages.Message):
    date = messages.MessageField(Date, 1)

class UploadUrl(messages.Message):
    url = messages.StringField(1)
    email = messages.StringField(2)

class VideoUrl(messages.Message):
    url = messages.StringField(1)
    user_nicknames = messages.StringField(2)

class VideoUrls(messages.Message):
    urls = messages.MessageField(VideoUrl, 1, repeated=True)

class Badge(messages.Message):
    badge = messages.StringField(1)
    points = messages.IntegerField(2)
    date = messages.MessageField(Date, 3)
        
class Badges(messages.Message):
    badges = messages.MessageField(Badge, 1, repeated=True)

class User(messages.Message):
    username = messages.StringField(1)
    email = messages.StringField(2)
    picture = messages.StringField(3)

class UserSummary(messages.Message):
    limit = messages.IntegerField(1, variant=messages.Variant.INT32)
    had_today = messages.IntegerField(2, variant=messages.Variant.INT32)
    pot = messages.IntegerField(3, variant=messages.Variant.INT32)
    user_nickname = messages.StringField(4)
    user = messages.MessageField(User, 5)
    had_lastndays = messages.IntegerField(6, variant=messages.Variant.INT32)
    is_low_risk = messages.BooleanField(7, variant=messages.Variant.BOOL)
    is_heavy = messages.BooleanField(8, variant=messages.Variant.BOOL)
    is_sober = messages.BooleanField(9, variant=messages.Variant.BOOL)
    is_moderate = messages.BooleanField(10, variant=messages.Variant.BOOL)
    is_unhealthy = messages.BooleanField(11, variant=messages.Variant.BOOL)
    is_binge = messages.BooleanField(12, variant=messages.Variant.BOOL)
    points = messages.IntegerField(13, variant=messages.Variant.INT32)

class Program(messages.Message):
    limit = messages.IntegerField(1, variant=messages.Variant.INT32)
    had_today = messages.IntegerField(2, variant=messages.Variant.INT32)
    pot = messages.IntegerField(3, variant=messages.Variant.INT32)
    user_nickname = messages.StringField(4)
    movable = messages.StringField(5)
    moneyback = messages.IntegerField(6, variant=messages.Variant.INT32)
    joker = messages.StringField(7)
    n_joker_left = messages.IntegerField(8, variant=messages.Variant.INT32)
    username = messages.StringField(9)
    user = messages.MessageField(User, 10)
    had_lastndays = messages.IntegerField(11, variant=messages.Variant.INT32)
    is_low_risk = messages.BooleanField(12, variant=messages.Variant.BOOL)
    is_heavy = messages.BooleanField(13, variant=messages.Variant.BOOL)
    points = messages.IntegerField(14, variant=messages.Variant.INT32)

class FollowedUsers(messages.Message):
    summaries = messages.MessageField(UserSummary, 1, repeated=True)

class Balance(messages.Message):
    user_nickname = messages.StringField(2)
    pot = messages.IntegerField(1, variant=messages.Variant.INT32)
    cutoff_date = messages.MessageField(Date, 3)


class UserPotHistory(messages.Message):
    user_balance_history = messages.MessageField(Balance, 1, repeated=True)


class PotHistory(messages.Message):
    balance_history = messages.MessageField(UserPotHistory, 1, repeated=True)


class HistoryByDay(messages.Message):
    drinks = messages.IntegerField(1, variant=messages.Variant.INT32, repeated=True)
    limits = messages.IntegerField(2, variant=messages.Variant.INT32, repeated=True)
    
class NotificationSubscription(messages.Message):
    key = messages.StringField(1)
    is_subscribed = messages.BooleanField(2, variant=messages.Variant.BOOL)


@endpoints.api(name='balance', version='v1',
               allowed_client_ids=[WEB_CLIENT_ID, ANDROID_CLIENT_ID,
                                   IOS_CLIENT_ID, endpoints.API_EXPLORER_CLIENT_ID],
               audiences=[ANDROID_AUDIENCE],
               scopes=[endpoints.EMAIL_SCOPE])
class BalanceApi(remote.Service):
    """Balance API v1."""
    PROGRAM_RESOURCE = endpoints.ResourceContainer(
        Drink,
        date=messages.MessageField(Date, 1),
        joker=messages.StringField(2),
        email=messages.StringField(3),
        nDrinks=messages.IntegerField(4))
    
    STATS_RESOURCE = endpoints.ResourceContainer(
        start_date=messages.MessageField(Date, 1),
        end_date=messages.MessageField(Date, 2),
        email=messages.StringField(3),
        nDrinks=messages.IntegerField(4))
     
    SUBSCRIPTION_RESOURCE = endpoints.ResourceContainer(
        endpoint = messages.StringField(1),
        is_subscribed = messages.BooleanField(2, variant=messages.Variant.BOOL))
    
    PUSH_NOTIFY_RESOURCE = endpoints.ResourceContainer(
        user_nickname = messages.StringField(1))
    
    USER_RESOURCE = endpoints.ResourceContainer(
        user = messages.MessageField(User, 1))
   
    def parse_token(self, authorization):
        token = authorization.split()[1]
        return jwt.decode(token, settings.TOKEN_SECRET)

    def authenticate(self):

        user_instance = None
        authorization = os.getenv('HTTP_AUTHORIZATION')
        if not authorization:
            raise endpoints.UnauthorizedException('Missing authorization header')

        try:
            payload = self.parse_token(authorization)
        except DecodeError:
            raise endpoints.UnauthorizedException('Invalid token.')
        except ExpiredSignature:
            raise endpoints.UnauthorizedException('Token has expired')

        user_id = payload['sub']
        user_instance = models.User.get_by_id(user_id)
        
        if not user_instance:
            raise endpoints.UnauthorizedException('Not a registered user')
        
        return user_instance
    
    def build_user_info(self, user_instance, date):
        
        had_today = user_instance.had_today(date)
        points = user_instance.get_points(date,CUTOFF_DATE)
        user = User(username=user_instance.name,
                    email=user_instance.email,
                    picture = user_instance.picture)
        
        user_info =  Program(had_today=had_today,
                             user_nickname=user_instance.name[0:3],
                             username=user_instance.name,
                             user=user,
                             points=points)
        
        return user_info
    
    def build_users_summary(self, user, date):
               
        users_summary = []
        
        users = models.User.all()
        for u in users:
            had_today = u.had_today(date)
            had_lastndays = u.had_lastndays(date)
            points = u.get_points(date,CUTOFF_DATE)
            user = User(username=u.name,
                    email=u.email,
                    picture = u.picture)
            is_low_risk = u.is_low_risk(date)
            is_heavy = u.is_heavy(date)
            is_binge = u.is_binge(None,date)
            is_moderate = u.is_moderate(None,date)
            is_unhealthy = u.is_unhealthy(None,date)
            is_sober = u.is_sober(None,date)
            users_summary.append(UserSummary(had_today=had_today,
                                     had_lastndays = had_lastndays,
                                     user_nickname=u.name[0:3],
                                     is_low_risk=is_low_risk,
                                     is_heavy=is_heavy,
                                     is_binge=is_binge,
                                     is_moderate=is_moderate,
                                     is_sober=is_sober,
                                     is_unhealthy=is_unhealthy,
                                     user=user,
                                     points=points))
        
        return users_summary

    @endpoints.method(PROGRAM_RESOURCE, Program,
                      path='drink/add', http_method='POST',
                      name='drink.add')
    def drink_add(self, request):
            
        user_instance = self.authenticate()
        
        date = request.date
        if date:
            date = datetime.datetime(date.year, date.month, date.day)
            
        nDrinks = 1
        if request.nDrinks:
            nDrinks = request.nDrinks
        
        for i in range(nDrinks):
            user_instance.add(date)

        user_info = self.build_user_info(user_instance, date)

        try:
            return user_info
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(USER_RESOURCE, User,
                      path='user/put', http_method='POST',
                      name='user.put')
    def put_user(self, request):

        user_instance = self.authenticate()
 
        if not(user_instance):
            user_instance = models.User(email=current_user.email().lower(),
                                        name=current_user.nickname())
            user_instance.create()
        else:
            user_instance.email = request.user.email.lower()
            user_instance.name = request.user.username
            if request.user.picture:
                user_instance.picture = request.user.picture
            user_instance.put()
        
        try:
            return User(username=user_instance.name,
                        email=user_instance.email)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(USER_RESOURCE, User,
                      path='user/get', http_method='GET',
                      name='user.get')
    def get_user(self, request):

        user_instance = self.authenticate()
        
        try:
            return User(username=user_instance.name,
                        email=user_instance.email,
                        picture=user_instance.picture)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(PROGRAM_RESOURCE, User,
                      path='user/request', http_method='POST',
                      name='user.request')
    def user_request(self, request):

        user_instance = self.authenticate()

        if not user_instance:
            user_instance = models.NewUser.all().filter("email =", current_user.email()).get()

        if not user_instance:
            user_instance = models.NewUser(email=current_user.email(),
                                        name=current_user.nickname(),
                                        user_id = current_user.user_id()
                                        )
            user_instance.put()
            user_instance.notify()
        try:
            return User(name=user_instance.name,
                        email=user_instance.email,
                        user_id=user_instance.user_id)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')


    @endpoints.method(SUBSCRIPTION_RESOURCE, NotificationSubscription,
                      path='user/subscription', http_method='POST',
                      name='user.subscription')
    def susbcribe_notification(self, request):
 
        user_instance = self.authenticate()
 
        endpoint = request.endpoint
        is_subscribed = request.is_subscribed
 
        if endpoint.startswith('https://android.googleapis.com/gcm/send'):
            endpointParts = endpoint.split('/')
            registrationId = endpointParts[len(endpointParts) - 1]
            endpoint = 'https://android.googleapis.com/gcm/send'
    
        notification_subscription = models.NotificationSubscription(user = user_instance,
                                    subscription_key = registrationId
                                    )
        
        if is_subscribed:
            notification_subscription.subscribe()
            is_subscribed = True
        else:
            notification_subscription.unsubscribe() 
            is_subscribed = False
 
        try:
            return NotificationSubscription(is_subscribed=is_subscribed)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')
        
    @endpoints.method(PUSH_NOTIFY_RESOURCE, Program,
                      path='user/push_notify', http_method='POST',
                      name='user.push_notify')
    def push_notification(self, request):
 
        user_instance = self.authenticate()
 
        user_nickname = request.user_nickname
        
        user_to_notify = models.User.all().filter("name =", user_nickname).get()
        user_to_notify.push_notify()
 
        try:
            return Program()
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(PROGRAM_RESOURCE, Program,
                      path='pot/get_status', http_method='GET',
                      name='pot.getStatus')
    def get_status(self, request):

        user_instance = self.authenticate()

        date = request.date
        if date:
            date = datetime.datetime(date.year, date.month, date.day)

        user_info = self.build_user_info(user_instance, date)

        try:
            return user_info
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')
        
    @endpoints.method(PROGRAM_RESOURCE, FollowedUsers,
                      path='pot/get_followed_users', http_method='GET',
                      name='pot.getFollowedUsers')
    def get_followed_users(self, request):

        user_instance = self.authenticate()

        date = request.date
        if date:
            date = datetime.datetime(date.year, date.month, date.day)

        users = self.build_users_summary(user_instance, date)

        try:
            return FollowedUsers(summaries=users)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(PROGRAM_RESOURCE, PotHistory,
                      path='pot/get_history', http_method='GET',
                      name='pot.getHistory')
    def get_pot_history(self, request):

        user_instance = self.authenticate()

        date = request.date
        if date:
            date = datetime.datetime(date.year, date.month, date.day)

        balance_history = []
        all_users = models.User.all()
        for u in all_users:
            pot = models.Pot.all().filter("user =", u).get()
            cutoff = models.START_OF_PROGRAM
            user_balance_history = []
            while cutoff < models.CUTOFF_DATE:
                temp_cutoff = cutoff + datetime.timedelta(days=93)
                new_cutoff = datetime.datetime(temp_cutoff.year, temp_cutoff.month, 1, 0, 0, 0)
                money = pot.get_balance_history(u, cutoff, new_cutoff)
                cutoff = new_cutoff
                user_balance_history.append(
                    Balance(cutoff_date=Date(year=new_cutoff.year, month=new_cutoff.month, day=new_cutoff.day),
                            pot=money,
                            user_nickname=u.name[0:3]))

            balance_history.append(UserPotHistory(user_balance_history=user_balance_history))

        # user_balance_history=[Balance(pot=20,user_nickname="TFB")]
        # balance_history = [UserPotHistory(user_balance_history=user_balance_history)]

        try:
            return PotHistory(balance_history=balance_history)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(PROGRAM_RESOURCE, HistoryByDay,
                      path='pot/get_history_by_day', http_method='GET',
                      name='pot.getHistoryByDay')
    def get_history_by_day(self, request):

        date = request.date
        if date:
            date = datetime.datetime(date.year, date.month, date.day)

        user_instance = self.authenticate()
       
        username = request.email 
        user_instance = models.User.all().filter("name =", username).get()

        pot = models.Pot.all().filter("user =", user_instance).get()
        drinks, limits = pot.get_history(user_instance, date)

        try:
            return HistoryByDay(drinks=drinks,
                                limits=limits)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(STATS_RESOURCE, Stats,
                      path='pot/advanced_stats', http_method='GET',
                      name='pot.advancedStats')
    def advanced_stats(self, request):
        
        start_date = request.start_date
        end_date = request.end_date
        if start_date:
            start_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
        if end_date:
            end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)

        #user_instance = self.authenticate()
       
        email = request.email
        user_instance = models.User.all().filter("email =", email).get()

        pot = models.Pot.all().filter("user =", user_instance).get()
        stats = pot.advanced_stats(user_instance,start_date,end_date)

        try:
            return Stats(n_drinks=str(stats['number of drinks']),
                         weekly_average=str(stats['weekly average']),
                         sober_hours=str(stats['sober hours']),
                         UI_hours = str(stats['UI hours']),
                         UI_percent = str(stats['UI percent']),
                         UI_hours_per_week = str(stats['UI hours per week']),
                         owes=str(stats['owes']),
                         points=str(stats['points']))
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(STATS_RESOURCE, Badges,
                      path='user/redeem_badges', http_method='POST',
                      name='user.redeemBadges')        
    def redeem_badges(self, request):
        
        start_date = request.start_date
        end_date = request.end_date
        if start_date:
            start_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
        if end_date:
            end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)

        user = self.authenticate()
       
        #email = request.email
        #user = models.User.all().filter("email =", email).get()
        
        if request.nDrinks:
            nDrinks = request.nDrinks
            user.delete_drinks(end_date)
            for i in range(nDrinks):
                user.add(end_date)

        badges = user.redeem_badges(end_date,start_date)

        try:
            return Badges(badges=badges)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(PROGRAM_RESOURCE, UploadUrl,
                      path='get_upload_url', http_method='GET',
                      name='getUploadUrl')
    def get_video_url(self, request):

        user_instance = self.authenticate()

        upload_url = blobstore.create_upload_url('/upload_video')

        try:
            return UploadUrl(url=upload_url,
                             email=user_instance.email)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(PROGRAM_RESOURCE, VideoUrls,
                      path='get_video_urls', http_method='GET',
                      name='getVideoUrls')
    def get_video_urls(self, request):

        user_instance = self.authenticate()

        video_query = models.Video.query().order(-models.Video.time)

        urls = []
        user_nicknames = []
        for video in video_query.fetch(5):
            url = VideoUrl(url='/video/%s' % video.blob_key,user_nicknames=models.User.all().filter('email =', video.email).get().name)
            urls.append(url)

        try:
            return VideoUrls(urls=urls)
        
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

    @endpoints.method(PROGRAM_RESOURCE, Message,
                      path='upgrade', http_method='GET',
                      name='upgrade')
    def upgrade(self, request):

        #user_instance = self.authenticate()
        badge = models.Badge.all().get()
        message = "Badges exist already"
        if not(badge):
            badge = models.Badge()
            badge.init()
            message = "Badges created"

        try:
            return Message(message=message)
        except (IndexError, TypeError):
            raise endpoints.NotFoundException('Error')

app = endpoints.api_server([BalanceApi])
