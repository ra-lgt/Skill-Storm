import pyrebase
import pymongo
import firebase_admin
from firebase_admin import credentials, auth
class Configurations:
  Gaming=['Gaming','Gaming_2','Gaming_3']
  Technology=['Technology','Technology_2','Technology_3']
  Fitness=['fitness','fitness_2','fitness_3']
  Music=['Music','Music_2','Music_3']
  Photography=['Photography','Photography_2','Photography_3']

  
  firebaseConfig = {
  "apiKey": "AIzaSyBcZIhgtAzpRKAC0jXU6b1dPyoJw0ncjZE",

  "authDomain": "skill-storm-9b234.firebaseapp.com",

  "databaseURL": "https://skill-storm-9b234-default-rtdb.firebaseio.com",

  "projectId": "skill-storm-9b234",

  "storageBucket": "skill-storm-9b234.appspot.com",

  "messagingSenderId": "224236008238",

  "appId": "1:224236008238:web:1b8ffc2fe55e2b3e0300bf",

  "measurementId": "G-15LQK6QCPW"
}
  firebase=pyrebase.initialize_app(firebaseConfig)
  cred = credentials.Certificate('creds.json')
  firebase_admin=firebase_admin.initialize_app(cred)

  client = pymongo.MongoClient("mongodb+srv://raviajay:raviajay.2003@chat.9aq3vwu.mongodb.net/")

  def Setup_auth(self):
    return self.firebase.auth()

  def Setup_DataBase(self):
    return self.firebase.database()

  def Setup_Storage(self):
    return self.firebase.storage()

  def Setup_admin_auth(self):
    return auth





