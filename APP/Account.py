from flask import Flask,url_for,redirect,render_template
import requests
from Config import Configurations
import os
import shutil
from withdraw import Withdraw

class Account:
	config=Configurations()
	database=config.Setup_DataBase()
	update_profile=config.Setup_Storage()
	client=config.client
	user_balance=Withdraw()

	def get_referal_details(self,email):
		user_data=self.database.child("Users").order_by_child('email').equal_to(email).get()
		temp=user_data.val()

		return temp[next(iter(temp))]['referal_id']







	def update_referal_id(self,referal_id,update):
		db=self.client['referals']
		collection=db['referal_ids']

		filter_criteria = {'referal_id': referal_id}

		cursor = collection.find({})
		balance=0

		for doc in cursor:
			if(doc['referal_id']==referal_id):
				balance=doc['balance']
				if(update==False):
					return balance

				elif(update==True):
					
					if(balance>=0):

						update_operation = {'$set': {'balance': balance-1}}

						collection.update_one(filter_criteria, update_operation)

		return -1

		


	def verify_referal(self,referal_id):
		user_data=self.database.child('Users').order_by_child('referal_id').equal_to(referal_id).get()
		if(len(user_data.val())!=0):
			return True
		return False



	def add_referal(self,referal_id):



		if(self.verify_referal(referal_id)==True):
			db=self.client['referals']
			collection=db['referal_ids']

			balance=self.update_referal_id(referal_id,False)
			

			if(balance>=0):
				filter_criteria = {'referal_id': referal_id}
				update_operation = {'$set': {'balance': balance+3}}
				collection.update_one(filter_criteria, update_operation)
				
			else:
				collection.insert_one({'referal_id':referal_id,'balance':3})





	def is_url_exists(self,url):
		response=requests.get(url)

		if(response.status_code==200):
			return True
		else:
			return False

	def get_user_name(self,email):
		user_data=self.database.child("Users").order_by_child('email').equal_to(email).get()
		temp=user_data.val()
		username=temp[next(iter(temp))]['username']

		return username

	def get_profile_pic(self,username):
		
		
		url=self.update_profile.child(username).get_url(None) or None

		if (not self.is_url_exists(url)):
			url=""

		return url


	

	def render_page(self,email,username,view=True):
		
		user_data=self.database.child("Users").order_by_child('email').equal_to(email).get()
		temp=user_data.val()

		payload={
		'username' : username,
		'email' : email,
		'url':None,
		'referal_id':temp[next(iter(temp))]['referal_id'],
		'title':[],
		'options':[],
		'Date':[],
		'image':[],
		'Type':[],
		'price':[]

		}
		database=self.client['user_contest_data']

		collection=database[email]

		documents=collection.find()
		if(documents is not None):

			for doc in documents:
				
				payload['title'].append(doc['title'])
				payload['options'].append(doc['options'])
				payload['image'].append(doc['URL'])
				payload['Date'].append(doc['Date'])
				payload['Type'].append(doc['Type'])
				payload['price'].append(doc['price'])


		payload['url']=self.get_profile_pic(username)
		balance=self.user_balance.get_user_balance(email)
		

		return render_template('author.html',data=payload,count=len(payload['options']),view=view,balance=balance)


	def update_profile_picture(self,file,email,username):
		update_profile=self.config.Setup_Storage()


		self.update_profile.child(username).put(file)

	
		return self.render_page(email,username)


	def get_email(self,contest_id):
		contest_data=self.database.child('Contest').child(contest_id).get()
		email=""

		for key_1,value_1 in contest_data.val().items():
				email=value_1.get('email')

		return email

