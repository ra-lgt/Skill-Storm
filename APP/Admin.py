from flask import Flask,url_for,redirect,render_template
from Config import Configurations
from Explore import Explore
from Chat import Chat
from Contest import Create_Contest
from datetime import datetime


class Admin:
	config=Configurations()
	explore=Explore()
	database=config.Setup_DataBase()
	mongo_conn=config.client
	chat=Chat()
	contest=Create_Contest()
	Contest_image=config.Setup_Storage()
	


	def render_page(self):
		return render_template('Admin_signup.html')

	def get_contest_data(self):
		all_joined_data={
		'username':[],
		'contest_id':[],
		'options':[],
		'title':[],
		'Date':[],
		'all_ids':[]	
		}

		joined=self.explore.get_contest_data(None,None,"Joined",None)
		Hosted=self.explore.get_contest_data(None,None,"Contest",None)


		if(joined!=None):
			for key,value in joined.items():
				for i in value:
					if key in all_joined_data:
						all_joined_data[key].append(i)
						if(key=='contest_id'):
							all_joined_data['all_ids'].append(i)

		if(Hosted!=None):
		
			for key,value in Hosted.items():
				for i in value:
					if(key=='contest_id'):
						if(i not in all_joined_data['all_ids']):
							all_joined_data['all_ids'].append(i)


		if(len(all_joined_data['all_ids'])==0):
			return False

		return all_joined_data


	def home_page(self):

		all_joined_data=self.get_contest_data()
		print(all_joined_data)
		if(all_joined_data==False):
			return render_template('Admin_home.html',contest=False)
		else:
			return render_template('Admin_home.html',data=all_joined_data,count=len(all_joined_data['contest_id']),contest=True)

	def delete_contest(self,contest_id):
		mongo_db=self.mongo_conn['Chats']

		user_data=mongo_db['user_data']

		query={'value':contest_id}

		user_data.delete_many(query)

		mongo_db[contest_id].drop()

		self.database.child("Joined").child(contest_id).remove()



	def admin_chat_page(self):
		temp=self.get_contest_data()
		if(temp==None):
			return "NO CHATS"


		contest_ids=temp['all_ids']

		return contest_ids

	def display_contest_page(self):
		return render_template('Admin_create.html')


	def create_contest(self,title,description,price,options):

		ids=self.contest.generate_random_string(5)

		database=self.mongo_conn['Free_contest']

		connection=database["contest_data"]
		current_date = datetime.now()

		connection.insert_one({
			'id':ids,
			'title':title,
			'description':description,
			'price':price,
			'options':options,
			'URL':self.Contest_image.child(options+".png").get_url(None) or None,
			'Date':current_date.strftime('%d-%B')

			})


	def display_free_contest(self):
		database=self.mongo_conn['Free_contest']

		datas={
		'id':[],
		'title':[],
		'description':[],
		'price':[],
		'options':[],
		'URL':[],
		'Date':[]
		}
		collection =database['contest_data']

		cursor=collection.find()

		for data in cursor:
			for key,value in data.items():

				if key not in datas:
					continue
				else:
					
					datas[key].append(value)

		return datas


	def get_free_data(self,contest_id):
		database=self.mongo_conn['Free_contest']
		collection =database['contest_data']

		data=collection.find({'id':contest_id})


		datas={
		'id':list(),
		'title':list(),
		'Description':list(),
		'price':list(),
		'options':list(),
		'URL':list(),
		'username':['Admin'],
		'Date':[]
		}
		for i in data:
			datas['id'].append(i['id'])
			datas['title'].append(i['title'])
			datas['Description'].append(i['description'])
			datas['price'].append(i['price'])
			datas['options'].append(i['options'])
			datas['URL'].append(i['URL'])
			datas['Date'].append(i['Date'])
			break

		return datas







