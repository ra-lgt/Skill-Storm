from flask import Flask,render_template,url_for
from Config import Configurations
from Account import Account
from Explore import Explore
#from Chat import Chat


class Items:
	account=Account()
	explore=Explore()
	

	def view_items_details(self,contest_id,email):
		contest_data={
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
		'profile_url':[]
		}
		user_name=self.account.get_user_name(email)
		profile_pic=self.account.get_profile_pic(email)
		result_data=self.explore.get_contest_data(email,contest_id,"Contest",None)
		emails=self.account.get_email(contest_id)

		index=result_data['contest_id'].index(contest_id)

		for key,value in result_data.items():
			contest_data[key].append(str(result_data[key][index]))


		return render_template('details.html',email=emails,data=contest_data,contest_id=contest_id,Admin=False)
