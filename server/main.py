import webapp2
import os
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template
from google.appengine.ext import blobstore
import settings
from model import models
import json
import jwt
import urllib
import datetime
from google.appengine.api import urlfetch

def create_token(user):
    
    payload = {
        'sub': user.key().id(),
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14)
    }
    token = jwt.encode(payload, settings.TOKEN_SECRET)
    return token.decode('unicode_escape')

class VideoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
#         try:
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")

        upload = self.get_uploads()[0]
        user_email = self.request.get('email')
        user_video = models.Video(blob_key=upload.key(),email=user_email)
        user_video.put()
        
        #self.redirect('/shame')
        
        return self.response

#         except:
#             self.redirect('/')

class ViewVideoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, video_key):
        
        #video_key = models.Video.query().get().blob_key
        if not blobstore.get(video_key):
            self.error(404)
        else:
            self.send_blob(video_key)#,save_as="shame.webm")
            
class MainPage(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../client/index.html')
        template_values = {
        }
        self.response.out.write(template.render(path, template_values))
        # self.response.headers['Content-Type'] = 'text/plain'
        # self.response.write('Hello, webapp2!')

class UserLoginHandler(webapp2.RequestHandler):
    def post(self):
        
        access_token_url = 'https://accounts.google.com/o/oauth2/token'
        people_api_url = 'https://www.googleapis.com/plus/v1/people/me/openIdConnect'
        
        params = json.loads(self.request.body)

        payload = dict(client_id=params['clientId'],
                       redirect_uri=params['redirectUri'],
                       client_secret=settings.GOOGLE_SECRET,
                       code=params['code'],
                       grant_type='authorization_code')
        
        payload = urllib.urlencode(payload)
        # Step 1. Exchange authorization code for access token.
        response = urlfetch.fetch(access_token_url, payload=payload, method=urlfetch.POST)
        content = json.loads(response.content)
        access_token = content['access_token']
        headers = {'Authorization': 'Bearer {0}'.format(access_token)}
    
        # Step 2. Retrieve information about the current user.
        response = urlfetch.fetch(people_api_url, headers=headers)
        profile = json.loads(response.content)
            

         # Step 4. Create a new account or return an existing one.
        email = profile['email']
        user_instance = models.User.all().filter("email =", email.lower()).get()
        if not(user_instance):
            user_instance = models.User(name=profile['name'],
                                 picture=profile['picture'],
                                 email=email.lower())
        user_instance.token = access_token
        user_instance.put()
        
        token = create_token(user_instance)

        self.response.headers['Content-Type'] = 'application/json'
        
        response = dict(token=token)
        self.response.write(json.dumps(response))
        
class SendEmailReminderHandler(webapp2.RequestHandler):
    def get(self):
        users = models.User.all()
        for user_instance in users:
            user_instance.send_drinkform_email()
        
        self.response.content_type = 'text/plain'
        self.response.write('Sent an email message to users not having entered their drinks.')
            
app = webapp2.WSGIApplication([('/upload_video',VideoUploadHandler),
                               ('/video/([^/]+)?', ViewVideoHandler),
                               ('/send_reminder', SendEmailReminderHandler),
                               ('/auth/google', UserLoginHandler),
                               ('/.*', MainPage),]
                               ,debug=settings.DEBUG)

def main():
    app.run()

if __name__ == '__main__':
    main()
