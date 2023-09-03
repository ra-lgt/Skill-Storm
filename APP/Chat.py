from Config import Configurations
from flask import Flask,url_for,redirect,render_template
from Config import Configurations
from Account import Account

class Chat:
	client=Configurations.client
	config=Configurations()
	account=Account()
	database=config.Setup_DataBase()
	Contest_image=config.Setup_Storage()

	def join_free_contest(self,contest_id,email,username,database):
		db=self.client["Free_contest"]

		collection=db["contest_data"]

		result_data=collection.find({'id':contest_id})

		for i in result_data:
			data={
				'email':email,
				'contest_id':i['id'],
				'Type':"Joined",
				'options':i['options'],
				'Date':i['Date'],
				'title':i['title'],
				'price':i['price'],
				'URL':self.Contest_image.child(i['options']+".png").get_url(None) or None,
				'username':username
				}
			self.database.child("Joined").child(contest_id).push(data)
			database.insert_one(data)

		collection.delete_one({'id':contest_id})

	def add_user(self,contest_id,email,username,Admin=False):

		
		Database=self.client['Chats']
		collection=Database[contest_id]


		

		user_data=Database['user_data']


		user_contest_data=self.client['user_contest_data']
		user_contest_join=user_contest_data[email]


		user_data.insert_one({"email": email, "value": contest_id,"Type":"Joined","username":username,"Free":Admin})

		
		#user_contest_join.insert_one({'email':email,"contest_id":contest_id,'Type':"Hosted"})


		
		data={'Admin':""}
		collection.insert_one(data)
		print((Admin))


		if(Admin=="True"):
			print("HELL")
			self.join_free_contest(contest_id,email,username,user_contest_join)

		else:
			print("FUCK")
			contest_data=self.database.child("Contest").child(contest_id).order_by_child('contest_id').equal_to(contest_id).get()
		#user_contest_join.insert_one({'email':email,"contest_id":contest_id,'Type':"Joined"})

			self.database.child("Contest").child(contest_id).remove()

			for key,value in contest_data.val().items():
				self.database.child("Joined").child(contest_id).push(value)
			
				data={
				'email':value['email'],
				'contest_id':value['contest_id'],
				'Type':"Joined",
				'options':value['options'],
				'Date':value['Date'],
				'title':value['title'],
				'price':value['price'],
				'URL':self.Contest_image.child(value['options']+".png").get_url(None) or None
				}
				user_contest_join.insert_one(data)
				break



	def get_user_chat(self,email):
		Database=self.client['Chats']
		

		user_data=Database['user_data']
		query = {"email": email}
		selected_documents = user_data.find(query)

		contest_ids = [doc["value"] for doc in selected_documents]

		print(contest_ids)
		


		return contest_ids 

	def get_history_chat(self,ids,Admin=False):
		data={
		'title':[],
		'URL':[],

		}
		for i in ids:
			print(i)
			try:
				user_data=None

				if(Admin==True):
					user_data=self.database.child("Contest").child(i).order_by_child('contest_id').get()
				elif(Admin==False):
					user_data=self.database.child("Contest").child(i).order_by_child('contest_id').equal_to(i).get()
				
				for key, values in user_data.val().items():
					data['title'].append(values.get("title"))
					option=values.get('options')
					temp=self.Contest_image.child(option+".png").get_url(None) or None 
					data['URL'].append(temp)


			except:
				user_data=None
				if(Admin==True):
					user_data=self.database.child("Joined").child(i).order_by_child('contest_id').get()
				elif(Admin==False):
					user_data=self.database.child("Joined").child(i).order_by_child('contest_id').equal_to(i).get()
				
				print(user_data.val())
				for key, values in user_data.val().items():

					if(values.get("title") in data['title']):
						continue
					else:
						data['title'].append(values.get("title"))
						option=values.get('options')
						temp=self.Contest_image.child(option+".png").get_url(None) or None 
						data['URL'].append(temp)

		return data

	def specific_chats(self,ids):
		database=self.client["Chats"]
		collection=database[ids]

		user_names_contest=database['user_data']

		query={'value':ids}
		document=user_names_contest.find(query)



		chats={
		
		'message':[],
		'time':[],
		'username':[]

		}
		cursor = collection.find()
		count=0

		for i in cursor:
			if("Admin" not in i):
			
				chats['message'].append(i['message'])
				chats['time'].append(i['time'])

		for i in document:
			chats['username'].append(i['username'])

		return chats


				
	
	def render_chat_page(self,data,email,ids,current_id,title,url,Admin=False):
		user_name="Admin"
		file='chat'

		if(Admin==False):
			user_name=self.account.get_user_name(email)
		
		value=zip(data['title'],ids,data['URL'])

		
		

		
		contest_chat=self.specific_chats((current_id))

		chats=zip(contest_chat['time'],contest_chat['message'])

		contest_chat['username'].append('')
		
		if(Admin==True):
			file='Admin_chat'

		return render_template((file+'.html'),value=value,username=user_name,contest_chat=chats,title=title,url=url,participants=contest_chat['username'],contest_id=current_id)

	

		






			
		

