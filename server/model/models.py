'''
Created on Dec 18, 2010

@author: t-bone
'''
from google.appengine.ext import db
from google.appengine.ext import ndb
import datetime
from google.appengine.api import mail
from google.appengine.api import urlfetch
from settings import CUTOFF_DATE

COST = 10
GAIN = 5
UNLIMITED_GAIN = 50
CUTOFF_HOUR = 8
START_OF_PROGRAM = datetime.datetime(2013,01,01,0,0,0)
GCM_API_KEY = "AIzaSyAAlwHLo79CGuM7iHdKsm0vQ_ok4ka4rU8"
PUSH_URL = "https://android.googleapis.com/gcm/send"
DRINKS_PER_HOUR = 1.25
LR_WEEKLY = 14
LR_DAILY = 4
HEAVY_DAILY = 5
HEAVY_MONTHLY = 5
MODERATE = 2
BINGE = 8
BLACKOUT = 12
RCP_WEEKLY = 21
#Points
MODERATE_PTS = 1
BINGE_PTS = -5
BLACKOUT_PTS = -10
HEAVY_PTS = -1
SOBER_PTS = 3
LOW_RISK_PTS = 2
RCP_WEEKLY_PTS = -2

    
class User(db.Model):
    user_id = db.StringProperty()
    name = db.StringProperty(required=True)
    picture = db.StringProperty()
    email = db.StringProperty()
    token = db.StringProperty()

    def create(self):
        
        self.put()
        pot = Pot(user = self,
                  money = 0)
        pot.put()
        
    def push_notify(self):
        
        notification_subscription = NotificationSubscription.all().filter("user =",self).get()
        content = notification_subscription.push_notification()
        
        return content
    
    def send_reminder_email(self,date=None):
        
        pot = Pot.all().filter("user =",self).get()
        n_drinks = pot.had_lastndays(self, date, 2)
        
        if n_drinks==0:
        
            message = mail.EmailMessage(sender="thierry.ferland@gmail.com",
                                        subject="Enter your drinks")
            
            message.html = "<p>Dear " + self.name + ",</p><br><p>You didn't have a single drink over the last three days. The Program is impressed. Or would it be that you forgot to enter your drinks bitch?</p><br><p><a href='http://www.tgprogram.com'>Do It Now</a></p>" 
            to_addr =''
            message.to = self.email
            message.send()

    def send_drinkform_email(self,today=None):

        if not(today):
            today = datetime.datetime.now()
        
        yesterday = today - datetime.timedelta(days=1)
                    
        pot = Pot.all().filter("user =",self).get()
        n_drinks = pot.had_lastndays(self, yesterday, 1)
        
        url = "http://www.tgprogram.com/email?" + "year=" + str(yesterday.year) + "&month=" + str(yesterday.month) + "&day=" + str(yesterday.day) + "&nDrinks="
        variables= ()
        for i_urls in range(8):
            variables = variables + (url+str(i_urls+1),)
        variables = variables + ("http://www.tgprogram.com",)
        
        file = open('server/templates/drinkentry.html')
        html = file.read() % variables
        
        subject = "Enter your drinks for " + yesterday.strftime('%A, %B %d')
        
        if n_drinks==0:
        
            message = mail.EmailMessage(sender="theprogram@tgprogram.com",
                                        subject=subject)       
            
            message.html = html
            to_addr =''
            message.to = self.email
            message.send()               

    def get_badges(self,date):
        
        nDrinks = self.had_lastndays(date,1)
        is_sober = self.is_sober(nDrinks)
        is_binge = self.is_binge(nDrinks)
        is_moderate = self.is_moderate(nDrinks)
        is_heavy = self.is_heavy(date)
        is_low_risk = self.is_low_risk(date)
        is_unhealthy = self.is_unhealthy(None,date)
        badges = {'Sober':(is_sober,SOBER_PTS),
                  'Binge':(is_binge,BINGE_PTS),
                  'Moderate':(is_moderate,MODERATE_PTS),
                  'Heavy':(is_heavy,HEAVY_PTS),
                  'Low Risk':(is_low_risk,LOW_RISK_PTS),
                  'Unhealthy':(is_unhealthy,RCP_WEEKLY_PTS)}
        
        return badges
        
    def redeem_badges(self,date,start_date=None):
 
        if not(start_date):
            start_date = date
            
        user_badges = UserBadge.all().filter("date >=",start_date).filter("date <=",date).filter("user =",self)
        for badge in user_badges:
            badge.delete()
        
        n_badges = 0
        user_badges = []
        while date >= start_date:
            badges = self.get_badges(date)
            
            for k,v in badges.iteritems():
                if v[0]:
                    badge = Badge.all().filter("label =",k).get()
                    user_badge = UserBadge(badge=badge,
                                  date=date,
                                  user=self)
                    user_badge.put()
                    n_badges += 1
                    user_badges.append({'date': {'year':date.year,'month':date.month,'day':date.day},'badge':badge.label,'points':badge.points})
                    
            date -= datetime.timedelta(days=1) 
        
        return user_badges

    def get_points(self,date,start_date=None):
 
        if not(start_date):
            start_date = date
            
        badges = Badge.all()
        points = 0
        for badge in badges:
            user_badges = UserBadge.all().filter("date >=",start_date).filter("date <=",date).filter("badge =",badge).filter("user =",self)
            points += user_badges.count() * badge.points
        
        return points    
    
    def had_lastndays(self,date=None,n_days=7):
        
        if not(date):
            date = datetime.datetime.now()  
        today = datetime.datetime(date.year,date.month,date.day,0, 0, 0,0)
        n_days_ago = today + datetime.timedelta(days=-n_days)
            
        drinks = Drink.all().filter("user =",self).filter("time >",n_days_ago).filter("time <=",today)
        
        return drinks.count()
    
    def is_low_risk(self,date=None):

        last_7 = self.get_history(date,7)
        total = 0
        for drinks in last_7:
            if drinks > LR_DAILY:
                return False
            total += drinks
        
        if total > LR_WEEKLY:
            return False
        
        return True
    
    def is_unhealthy(self,nDrinks=None,date=None):

        if not(nDrinks):
            nDrinks = self.had_lastndays(date,7)
        if nDrinks > RCP_WEEKLY:
            return True
        
        return False

    def is_heavy(self,date=None):

        last_30 = self.get_history(date,30)
        occasions = 0
        for drinks in last_30:
            if drinks >= HEAVY_DAILY:
                occasions += 1
            if occasions >= HEAVY_MONTHLY:
                return True
        
        return False
    
    def is_sober(self,nDrinks=None,date=None):

        if not(nDrinks):
            nDrinks = self.had_lastndays(date,1)
        if nDrinks == 0:
            return True
        
        return False
    
    def is_moderate(self,nDrinks=None,date=None):

        if not(nDrinks):
            nDrinks = self.had_lastndays(date,1)
        if nDrinks <= MODERATE and nDrinks > 0:
            return True
        
        return False
    
    def is_binge(self,nDrinks=None,date=None):

        if not(nDrinks):
            nDrinks = self.had_lastndays(date,1)
        if nDrinks >= BINGE:
            return True
        
        return False 
    
    def get_history(self,date=None,n_days=7):
        
        if not(date):
            date = datetime.datetime.now()
        today = datetime.datetime(date.year,date.month,date.day,0, 0, 0,0) - datetime.timedelta(days=n_days-1)
        
        drinks = []
        
        for ix_dummy in range(n_days):
            drinks.append(self.had_today(today))
            today = today + datetime.timedelta(days=1)
        
        return drinks
    
    def had_today(self,date=None):
        
        return self.had_lastndays(date,1)
    
    def delete_drinks(self,date):
        
        drinks = Drink.all().filter("user =",self).filter("time >=",date).filter("time <=",date)
        for drink in drinks:
            drink.delete()
        return drinks.count()
    
    def add(self,date=None):
        
        if not(date):
            date = datetime.datetime.now()
            date = datetime.datetime.combine(date.date(),date.time())
        
        drink = Drink(user = self,
                      time = date)
        drink.put()


class NewUser(db.Model):
    user_id = db.StringProperty()
    name = db.StringProperty()
    email = db.StringProperty()

    def notify(self):

            message = mail.EmailMessage(sender="thierry.ferland@gmail.com",
                                subject="New User Request")

            message.body = "New Request from " + self.email + "!!!"
            to_addr = "thierry.ferland@gmail.com"

            message.to = to_addr
            message.send()

class Video(ndb.Model):
    
    email = ndb.StringProperty()
    time = ndb.DateTimeProperty(default=datetime.datetime.today())#required=True,
    blob_key = ndb.BlobKeyProperty(required=True)

class Drink(db.Model):

    user = db.ReferenceProperty(User,verbose_name='User',collection_name='user')
    time = db.DateTimeProperty(default=datetime.datetime.today())
    
class Badge(db.Model):
    label = db.StringProperty()
    points = db.IntegerProperty()
    
    def init(self):
        
        badges = {'Sober':SOBER_PTS,
          'Binge':BINGE_PTS,
          'Moderate':MODERATE_PTS,
          'Heavy':HEAVY_PTS,
          'Low Risk':LOW_RISK_PTS,
          'Unhealthy':RCP_WEEKLY_PTS}
        
        for k,v in badges.iteritems():
            badge = Badge(label=k,
                          points=v)
            badge.put()
    
    
class UserBadge(db.Model):
    user = db.ReferenceProperty(User,verbose_name='User',collection_name='user_badge')
    date = db.DateTimeProperty()
    badge = db.ReferenceProperty(Badge,verbose_name='Badge',collection_name='Badge_Badge')

class Movable(db.Model):

    label = db.StringProperty(required=True)
    nDrinks = db.IntegerProperty(required=True)
    joker = db.BooleanProperty()
    
    def was_called(self,user,date=None):
        
        if not(date):
            date = datetime.datetime.now()

        start_week = date - datetime.timedelta(days=date.weekday())
        start_week = datetime.datetime(start_week.year,start_week.month,start_week.day, 0, 0, 0,0) 
        end_week = start_week + datetime.timedelta(days=7)
        call = Call.all().filter("user =", user).filter("movable =", self).filter("time >=",start_week).filter("time <",end_week).get()
        if call:
            return True
        else:
            return False

    def n_time_called(self,user,date=None):

        if not date:
            date = CUTOFF_DATE
        n_call = Call.all().filter("user =", user).filter("movable =", self).filter("time >=",date).count()

        return n_call
    
class Call(db.Model):
    
    user = db.ReferenceProperty(User,verbose_name='User',collection_name='call_user')
    movable = db.ReferenceProperty(Movable,verbose_name='Movable',collection_name='call_movable')
    time = db.DateTimeProperty()
    
    def do(self,date,joker=None):
    
        pot = Pot.all().filter("user =",self.user).get()
        if not(pot):
            pot = Pot(user = self.user,
                            money = 0)
            pot.put()
        
        movable = pot.get_movable(self.user,date,joker)
       
        if movable:
            self.movable = movable
            self.put()
        
            #other_user = User.all().filter("user_id !=", self.user.user_id)
            other_user = User.all()
            
            #if other_user.count():
            message = mail.EmailMessage(sender=self.user.email,
                                        subject=movable.label)
            
            message.body = "I call " + movable.label + ", BIIIIITCH!!!" 
            to_addr =''
    
            for u in other_user:    
                to_addr = to_addr + u.email + ','
            message.to = to_addr
            message.send()
    
class DayGroup(db.Model):

    label = db.StringProperty(required=True)
    nDrinks = db.IntegerProperty(required=True)
    movable = db.ReferenceProperty(Movable,verbose_name='Movable day',collection_name='group_movable')
    
class Week(db.Model):

    monday = db.ReferenceProperty(DayGroup,verbose_name='Monday',collection_name='monday_group',required=True)
    tuesday = db.ReferenceProperty(DayGroup,verbose_name='Tuesday',collection_name='tuesday_group',required=True)
    wednesday = db.ReferenceProperty(DayGroup,verbose_name='Wednesday',collection_name='wednesday_group',required=True)
    thursday = db.ReferenceProperty(DayGroup,verbose_name='Thursday',collection_name='thursday_group',required=True)
    friday = db.ReferenceProperty(DayGroup,verbose_name='Friday',collection_name='friday_group',required=True)
    saturday = db.ReferenceProperty(DayGroup,verbose_name='Saturday',collection_name='saturday_group',required=True)
    sunday = db.ReferenceProperty(DayGroup,verbose_name='Sunday',collection_name='sunday_group',required=True)
    any_day = db.ReferenceProperty(DayGroup,verbose_name='Any day',collection_name='anyday_group',required=True)
    
class OverLimit(db.Model):
    
    user = db.ReferenceProperty(User,verbose_name='User',collection_name='over_user')
    limit = db.IntegerProperty()
    date = db.DateTimeProperty()
    
class UnderLimit(db.Model):
    
    user = db.ReferenceProperty(User,verbose_name='User',collection_name='under_user')
    limit = db.IntegerProperty()
    date = db.DateProperty()
    active = db.BooleanProperty()
    
class Pot(db.Model):

    
    user = db.ReferenceProperty(User,verbose_name='User',collection_name='pot_user')
    week = db.ReferenceProperty(Week,verbose_name='Week',collection_name='pot_week')
    money = db.IntegerProperty()
    n_joker = db.IntegerProperty()
   
    def limit(self,user,date=None):
        
        if not(date):
            date = datetime.datetime.now()
        today = datetime.datetime(date.year,date.month,date.day, 0, 0, 0,0) 
        day = today.strftime('%A')
        tomorrow = today + datetime.timedelta(days=1)
        calls = Call.all().filter("user =",user).filter("time >=",today).filter("time <",tomorrow)

        limit = None
        addon = 0
        for call in calls:
            if call.movable.joker:
                addon = addon + call.movable.nDrinks
            elif call:
                limit = call.movable.nDrinks

        pot = Pot.all().filter("user =",user).get()

        if not limit:
            limit = eval('pot.week.' + day.lower() + '.nDrinks')

        limit = limit + addon
            
        return limit
    
    def had_today(self,user,date=None):
        
        return self.had_lastndays(user,date,1)
    
    def had_lastndays(self,user,date=None,n_days=7):
        
        if not(date):
            date = datetime.datetime.now()  
        today = datetime.datetime(date.year,date.month,date.day,0, 0, 0,0)
        n_days_ago = today + datetime.timedelta(days=-n_days)
            
        drinks = Drink.all().filter("user =",user).filter("time >",n_days_ago).filter("time <=",today)
        
        return drinks.count()
    
    def movable(self,user=None,date=None):
        
        if not(date):
            date = datetime.datetime.now()

        day = date.strftime('%A')
        #day = "Monday"
        pot = Pot.all().filter("user =",user).get()
        
        if pot:
            movable_instance = eval('pot.week.' + day.lower() + '.movable')
            joker_instance = pot.week.any_day.movable
        else:
            return 'No pot'

        joker_left = max(pot.n_joker - joker_instance.n_time_called(user),0)
        
        if movable_instance and joker_instance and not(movable_instance.was_called(user,date)) and joker_left:
            return movable_instance.label, joker_instance.label, joker_left
        elif joker_instance and joker_left:
            return None, joker_instance.label, joker_left
        elif movable_instance and not(movable_instance.was_called(user,date)):
            return movable_instance.label, None, joker_left
        
        return None, None, joker_left
 
    def get_movable(self,user=None,date=None,joker=None):
        
        if not(date):
            date = datetime.datetime.now()

        day = date.strftime('%A')
        #day = "Monday"
        pot = Pot.all().filter("user =",user).get()
        
        if pot:
            if joker:
                joker_instance = pot.week.any_day.movable
                joker_left = max(pot.n_joker - joker_instance.n_time_called(user),0)
                if joker_instance and joker_left:
                    return joker_instance
            else:
                movable_instance = eval('pot.week.' + day.lower() + '.movable')

                if movable_instance and not(movable_instance.was_called(user,date)):
                    return movable_instance
        else:
            return None
        

        
        return None
    
    def balance(self,user):
            
        money = Pot.all().filter("user =",user).get().money
        
        return money
        
     
    def add(self,user,date=None):
        
        if not(date):
            date = datetime.datetime.now()
            date = datetime.datetime.combine(date.date(),date.time())
        
        drink = Drink(user = user,
                      time = date)
        drink.put()
        
        limit = self.limit(user,date)
        drinks = self.had_today(user,date)
        
        if drinks > limit:
            over_instance = OverLimit(user=user,limit=limit,date=date)
            over_instance.put()
            
        self.money = OverLimit.all().filter("user =",user).filter("date >=",CUTOFF_DATE).count() * COST - UnderLimit.all().filter("user =",user).filter("date >=",CUTOFF_DATE).filter("active =",True).count() * GAIN
        self.put()
        
    def get_balance_history(self,user,start_date,end_date):

        money = OverLimit.all().filter("user =",user).filter("date >=",start_date).filter("date <",end_date).count() * COST - UnderLimit.all().filter("user =",user).filter("date >=",start_date).filter("date <",end_date).filter("active =",True).count() * GAIN        
        
        return money

    def update(self,user):
 
        self.money = OverLimit.all().filter("user =",user).filter("date >=",CUTOFF_DATE).count() * COST - UnderLimit.all().filter("user =",user).filter("date >=",CUTOFF_DATE).filter("active =",True).count() * GAIN
        self.put()
    
    def money_back(self,user,date):
        
        if not(date):
            date = datetime.datetime.now()
        
        date = datetime.date(date.year,date.month,date.day)
        
        limit = self.limit(user,date)
        drinks = self.had_today(user,date)
        got_money = UnderLimit.all().filter("user =",user).filter("date =",date).count()
        money = 0
        iUnlimited = 0
        nUnlimited = UNLIMITED_GAIN/GAIN
        
        while not(got_money) and drinks < limit and iUnlimited < nUnlimited:
            
            nover = OverLimit.all().filter("user =",user).filter("date >=",CUTOFF_DATE).filter("date <",date + datetime.timedelta(days=1)).count()
            nunder = UnderLimit.all().filter("user =",user).filter("active =",True).filter("date >=",CUTOFF_DATE).filter("date <",date + datetime.timedelta(days=1)).count()
            
            if nover*COST > nunder*GAIN and self.money > 0:
                active = True
                money = money + GAIN
            else:
                active = False
                
            under_instance = UnderLimit(user=user,limit=limit,date=date,active=active)
            under_instance.put()
            
            drinks = drinks + 1
            
            #Unlimited nights cutoff
            if limit > 50:
                iUnlimited = iUnlimited + 1

        self.money = OverLimit.all().filter("user =",user).filter("date >=",CUTOFF_DATE).count() * COST - UnderLimit.all().filter("user =",user).filter("date >=",CUTOFF_DATE).filter("active =",True).count() * GAIN
        self.put()
        
        return money
    
    def get_history(self,user=None,date=None,n_days=7):
        
        if not(date):
            date = datetime.datetime.now()
        today = datetime.datetime(date.year,date.month,date.day,0, 0, 0,0) - datetime.timedelta(days=n_days)
        #tomorrow = today + datetime.timedelta(days=1)
        
        drinks = []
        limits = []
        
        for ix_dummy in range(n_days):
            drinks.append(self.had_today(user,today))
            limits.append(self.limit(user,today))
            today = today + datetime.timedelta(days=1)
        
        return drinks, limits
    
    def advanced_stats(self,user,start_date=CUTOFF_DATE,end_date=None):

        if not(start_date):
            start_date = CUTOFF_DATE
        
        if not(end_date):
            end_date = datetime.datetime.now()  
              
        results = {}
        time_delta = end_date-start_date
        days = time_delta.days
        hours = days * 24
        weeks = days / 7
        results['number of drinks'] = self.had_lastndays(user,end_date,days)
        results['weekly average'] = results['number of drinks'] / days * 7
        results['UI hours'] = results['number of drinks'] * DRINKS_PER_HOUR
        results['sober hours'] = hours - results['UI hours']
        results['UI percent'] = round(1. - results['sober hours'] / float(days * 24),3)*100
        results['owes'] = self.get_balance_history(user,start_date,end_date)
        results['UI hours per week'] = round(results['UI hours'] / weeks,1)
        results['points'] = self.get_points(user,end_date,start_date)
        
        return results
    
    def is_low_risk(self,user,date=None):

        last_7 = self.get_history(user,date,7)
        total = 0
        for drinks in last_7[0]:
            if drinks > LR_DAILY:
                return False
            total += drinks
        
        if total > LR_WEEKLY:
            return False
        
        return True
    
    def is_unhealthy(self,user,nDrinks=None,date=None):

        if not(nDrinks):
            nDrinks = self.had_lastndays(user,date,7)
        if nDrinks > RCP_WEEKLY:
            return True
        
        return False

    def is_heavy(self,user,date=None):

        last_30 = self.get_history(user,date,30)
        occasions = 0
        for drinks in last_30[0]:
            if drinks >= HEAVY_DAILY:
                occasions += 1
            if occasions >= HEAVY_MONTHLY:
                return True
        
        return False
    
    def is_sober(self,user,nDrinks=None,date=None):

        if not(nDrinks):
            nDrinks = self.had_lastndays(user,date,1)
        if nDrinks == 0:
            return True
        
        return False
    
    def is_moderate(self,user,nDrinks=None,date=None):

        if not(nDrinks):
            nDrinks = self.had_lastndays(user,date,1)
        if nDrinks <= MODERATE:
            return True
        
        return False
    
    def is_binge(self,user,nDrinks=None,date=None):

        if not(nDrinks):
            nDrinks = self.had_lastndays(user,date,1)
        if nDrinks >= BINGE:
            return True
        
        return False
    
    def get_badges(self,user,date):
        
        nDrinks = self.had_lastndays(user,date,1)
        is_sober = self.is_sober(user,nDrinks)
        is_binge = self.is_binge(user,nDrinks)
        is_moderate = self.is_moderate(user,nDrinks)
        is_heavy = self.is_heavy(user,date)
        is_low_risk = self.is_low_risk(user,date)
        is_unhealthy = self.is_unhealthy(user,None,date)
        badges = {'Sober':(is_sober,SOBER_PTS),
                  'Binge':(is_binge,BINGE_PTS),
                  'Moderate':(is_moderate,MODERATE_PTS),
                  'Heavy':(is_heavy,HEAVY_PTS),
                  'Low Risk':(is_low_risk,LOW_RISK_PTS),
                  'Unhealthy':(is_unhealthy,RCP_WEEKLY_PTS)}
        
        return badges
        
    def get_points(self,user,date,start_date=None):
 
        if not(start_date):
            start_date = date
        
        points = 0
        while date >= start_date:
            badges = self.get_badges(user,date)
            
            for k,v in badges.iteritems():
                if v[0]:
                    points += v[1]
                    
            date -= datetime.timedelta(days=1) 
        
        return points       
        
    
class NotificationSubscription(db.Model):
    
    user = db.ReferenceProperty(User,verbose_name='User',collection_name='notification_user')
    subscription_key = db.StringProperty()
    url = db.StringProperty()
    is_subscribed = db.BooleanProperty()
    
    def subscribe(self):
        
        #notification_subscription = NotificationSubscription.all().filter("user=",self.user).filter("subscription_key=",self.subscription_key).get()
        notification_subscription = NotificationSubscription.all().filter("user =",self.user).get()
        
        if not notification_subscription:
            notification_subscription = self
            
        notification_subscription.is_subscribed = True
        notification_subscription.subscription_key = self.subscription_key
        notification_subscription.put()
        
        return notification_subscription

    def unsubscribe(self):
        
        notification_subscription = NotificationSubscription.all().filter("user =",self.user).get()
        
        if not notification_subscription:
            notification_subscription = self
            
        notification_subscription.is_subscribed = False
        #notification_subscription.subscription_key = self.subscription_key
        notification_subscription.put()
        
        return notification_subscription
    
    def push_notification(self):
        
        #key = "APA91bHVJQhsXFz73yra6Ln1i3oViBVL77Tjom8wUv4hHnCBIa4v8Q9sB32DrCkiodwygPofolZXdXdoFTGRYhXVhKH-TtSqI2T7c2k4apTYtnOrSnc5e86Srar_A42urDocwKJYWwkqjWAL268iORtJDpv90VWy6g9daZx3v182hGpPGfukvqE";
        data = "{"+"\"to\"" + ":" + "\"" + self.subscription_key + "\"" + "}";

        result = urlfetch.fetch(url=PUSH_URL,
                                payload=data,
                                method=urlfetch.POST,
                                headers={'Content-Type': 'application/json', 'Authorization': 'key=' + GCM_API_KEY})
        
        content = result.content
        
        return content

        
