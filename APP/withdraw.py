from flask import Flask,url_for,redirect,render_template
from Config import Configurations




class Withdraw():
	config=Configurations()
	client=config.client
	balance_db=client['users_cash_balance']
	collection=balance_db['balance']
	

	def render_page(self,username,email):
		balance=self.get_user_balance(email)

		return render_template('withdraw.html',data={"username":username,"email":email,"balance":balance})

	def get_user_balance(self,email,username=None):
		
		query={}
		if(username!=None):
			query['username']=username
		else:
			query['email']=email

		document = self.collection.find_one(query)

		balance=document.get("Balance")
		return balance


	def generate_user_register_balance(self,username,email):
		self.collection.insert_one({'username':username,'email':email,'Balance':0})



	def winner_add_balance(self,username,cash_price,contest_id):
		from Admin import Admin
		admin=Admin()

		
		query={"username":username.strip(),}
		update_operation = {'$set': {'Balance':float(float(self.get_user_balance(None,username))+(1.7*float(cash_price)))} }

		updated_document = self.collection.find_one_and_update(query, update_operation, return_document=True)
		admin.delete_contest(contest_id,"Joined")

	def reduce_balance(self,email,withdraw_amount,balance):
		query={"email":email.strip()}
		update_operation={"$set":{"Balance":(balance-withdraw_amount)}}
		updated_document = self.collection.find_one_and_update(query, update_operation, return_document=True)




	def withdraw_users_balance(self,email,Type,details):
		balance=self.get_user_balance(email)

		if(float(details['amount'])<=balance):
			collection=self.balance_db[Type]
			details['email_id']=email
			details['Type']=Type
			collection.insert_one(details)
			self.reduce_balance(email,float(details['amount']),float(balance))
			return True
		else:
			return False



		





