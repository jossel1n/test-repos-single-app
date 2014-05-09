"""Part 1 of the training session."""
import os

import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.


DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
  return ndb.Key('Guestbook', guestbook_name)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Greeting(ndb.Model):
  author = ndb.UserProperty()
  content = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

  def get(self):
    guestbook_name = self.request.get('guestbook',
                                      DEFAULT_GUESTBOOK_NAME)
    greetings_query = Greeting.query(
        ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
    greetings = greetings_query.fetch(10)

    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template = jinja_environment.get_template('index.html')
    self.response.out.write(template.render(greetings=greetings,
                                            url=url,
                                            url_linktext=url_linktext,
                                            guestbook_name=guestbook_name))


class Guestbook(webapp2.RequestHandler):

  def post(self):
    guestbook_name = self.request.get('guestbook', DEFAULT_GUESTBOOK_NAME)
    greeting = Greeting(parent=guestbook_key(guestbook_name))

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/?guestbook='+guestbook_name)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)
