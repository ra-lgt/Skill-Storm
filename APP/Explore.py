from flask import Flask,redirect,render_template,url_for
from Config import Configurations
from Account import Account


class Explore:

#Header Files
	config=Configurations()
	database=config.Setup_DataBase()
	Contest_image=config.Setup_Storage()
	account=Account()
	
	profile_url=""

	def search_page(self,email,page_no,filter):
		data=self.get_contest_data(email,None,"Contest",filter)
		if(data==None):
			return render_template('404.html',error="No contest at the moment:( ")
		end=min(len(data['options']),page_no*10)
		start=(page_no-1)*1
		prev=True
		nexts=True


		if(page_no==1):
			prev=False

		if(len(data['options'])<=end):
			nexts=False

		return render_template('search_contest.html',data=data,start=start,end=end,page_no=page_no,nexts=nexts,prev=prev)




#It gets the contest data for displaying and returns dictionary
	def get_contest_data(self,email,contest_id,Type,filter):
		result_data={
		"contest_id":[],
		"title":[],
		"Description":[],
		"username":[],
		'price':[],
		'royalities':[],
		'options':[],
		'Type':[],
		'URL':[],
		'Date':[],
		'profile_url':[],
		'criteria':[],
		'Joinee_username':[]
		}
		is_contest_exists=True

		if(self.database.child(Type).get().val()==None):
			return None
		if(contest_id==None):


			contest_data=self.database.child(Type).get()
			if(contest_data.val()!=None):
				for key_1,value_1 in contest_data.val().items():
					for key,value in value_1.items():
						if(value['email']==email):
							continue
						for keys,values in value.items():
							#print(value['options'][0:len(value['options'])-2:])
							


							if(filter==None or (value['options'][0:len(value['options'])-2:]==filter['options'] or value['title']==filter['title'])):

								if(keys in result_data):
									result_data[keys].append(values)
			else:
				is_contest_exists=False

		else:
			contest_data=self.database.child(Type).child(contest_id).get()
			for key_1,value_1 in contest_data.val().items():
				for keys,values in value_1.items():
					if(keys in result_data):
						result_data[keys].append(values)


		
		


		

		
		for image in result_data['options']:
			temp=self.Contest_image.child(image+".png").get_url(None) or None 
			result_data['URL'].append(temp)

		for pic in result_data['username']:
			url=self.Contest_image.child(pic).get_url(None) or None
			if (not self.account.is_url_exists(url)):
				url=""
			result_data['profile_url'].append(url)
					

		return result_data


#it gets contest data using email and contest_id=None

	def render_page(self,email,page_no):
		data=self.get_contest_data(email,None,"Contest",None)
		if(data==None):
			return render_template('404.html',error="No contest at the moment:( ")
		end=min(len(data['options']),page_no*10)
		start=(page_no-1)*1
		prev=True
		nexts=True


		if(page_no==1):
			prev=False

		if(len(data['options'])<=end):
			nexts=False

		



		return render_template('explore.html',data=data,start=start,end=end,page_no=page_no,nexts=nexts,prev=prev)