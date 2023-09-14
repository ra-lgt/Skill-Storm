from flask import Flask,url_for,redirect,render_template
from Config import Configurations
from Account import Account

class Notifications:
	config=Configurations()
	database=config.Setup_DataBase()
	profile_pic=config.Setup_Storage()
	account=Account()

#it gets notifications in firebase based on the username 

	def  get_notification(self,email,username):
		payload={
			'data':[]
			}
		

		if(email !=""):

			notify=self.database.child(username).get()

			for i in notify.val().items():
				for value in i:
					if("notification" in value):
						payload['data'].append(value['notification'])

		return payload

	def show_notifications_page(self):
		data={
		'email':[],
		'phone':[],
		'username':[],
		'URL':[]
		}
		collection=self.database.child("Users").get()
		for i in collection:
			
			data['email'].append(i.val()['email'])
			data['phone'].append(i.val()['phone'])
			data['username'].append(i.val()['username'])
			data['URL'].append(self.account.get_profile_pic(i.val()['username']))
		
		
		return render_template('push_notifications.html',data=data,count=len(data['email']))


	def push(self,data,username):
		self.database.child(username).push({'notification':data})



			
