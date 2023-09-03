from flask import Flask,render_template,request,url_for,redirect
from Config import Configurations
import random
import string
import requests
from datetime import datetime
from Payment import Payment


class Create_Contest:
	config=Configurations()
	database=config.Setup_DataBase()
	payment=Payment()
	client=config.client	
	Contest_image=config.Setup_Storage()


	def render_page(self,username):
		print(username)
		return render_template('create.html',username=username)

	def generate_random_string(self,length):
		characters = string.ascii_letters + string.digits 
		random_string = ''.join(random.choice(characters) for _ in range(length))
		return random_string




	def push_user_data(self,title,description,username,price,royalities,options,email):

		payload={
		'contest_id':self.generate_random_string(5),
		'title':title,
		'Description':description,
		'username':username,
		'price':price,
		'royalities':royalities,
		'options':options,
		'Type':'Hosted',
		'Date':"",
		'email':email
		
		}
		current_date = datetime.now()
		payload['Date']=current_date.strftime('%d-%B')


		self.database.child("Contest").child(payload['contest_id']).push(payload)
		
		
		Database=self.client['Chats']
		contest_id=payload['contest_id']
		collection = Database[contest_id]

		user_data=Database['user_data']
		print(email,contest_id)


		user_data.insert_one({"email": email, "value": contest_id,'Type':"Hosted","username":username,"title":title,"Free":False})

		user_databse=self.client['user_contest_data']
		user_contest_join=user_databse[email]

		user_contest_join.insert_one({'email':email,
			"contest_id":contest_id,
			'Type':"Hosted",
			'title':payload['title'],
			'options':payload['options'],
			'Date':payload['Date'],
			'price':price,

			'URL':self.Contest_image.child(payload['options']+".png").get_url(None) or None})

		return render_template('success.html',data="Your contest created successfully")
		

		

		

		





#self.database.child("Contest").push(payload)
		

		
			#return render_template('success.html',data="Your contest created successfully")