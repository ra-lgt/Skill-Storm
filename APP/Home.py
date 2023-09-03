from flask import Flask,render_template,request,session,redirect,url_for,make_response,jsonify
from Config import Configurations
from Contest import Create_Contest
from Explore import Explore
from Account import Account
from notification import Notifications
from Items import Items
from QrCode import Qr_Code
from Chat import Chat
from flask_socketio import SocketIO, emit,join_room,leave_room,send
import datetime
import threading
from Admin import Admin
from Cyberbullying import Cyberbullying
from functools import wraps
from send_mail import Send_Mail
from mycontest import MyContest
from forum import Forum
from Payment import Payment
from flask_cors import CORS

# Initialize the Firebase Admin SDK


#All Files are imported

date_time=datetime.datetime.now()
cyber=Cyberbullying()
payment=Payment()
config=Configurations()
auth=config.Setup_auth()
admin_auth=config.Setup_admin_auth()

app=Flask(__name__,static_folder='static')
CORS(app, resources={r"/bank_pay_host": {"origins": "https://checkout.stripe.com"}})

cookie=""
payload={
			'session':"",
			'email':'',
			'username':"",
			"current_contest_id":""
	}
acc=Account()
contest=Create_Contest()
exp=Explore()
database=config.Setup_DataBase()
items=Items()
qrcode=Qr_Code()
chat=Chat()
socketio = SocketIO(app)
app.secret_key = 'Skill-Storm'
client=Configurations.client
admin=Admin()
mail=Send_Mail()
my_contest=MyContest()
forums=Forum()
import random
#creating a reference
#------------------------------------------------------------------------------#

#home page it sends request to notifications to get data from notifications
#if there is no session means it doesn't show any bars
def generate_otp():
	sequence_length = 5
	min_value = 10 ** (sequence_length - 1)  # Smallest 5-digit number (10000)
	max_value = (10 ** sequence_length) - 1  # Largest 5-digit number (99999)
	random_number = random.randint(min_value, max_value)
	return random_number

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',error=None,solution=None), 404

def login_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        
        
        if session.get('user_id'):
            return view_function(*args, **kwargs)
        else:
            return redirect(url_for('signup_login'))
    return decorated_function

@app.route("/",endpoint="Home")
def Home():
	user_not={
	'data':[]
	}
	payload={
	'session':""

	}
	if('user_id' in session):

		notify=Notifications()
		temp=session.get('email')
		user_not=notify.get_notification(temp,session.get('username'))
		payload['session']=session.get('user_id')

	free_contest=admin.display_free_contest()
	print(free_contest)
	
	
	return render_template('index.html',data=payload,notification=user_not,count=len(user_not['data']),free_contest=free_contest,free_count=len(free_contest['id']))

#------------------------------------------------------------------------------#

#login page which signin's the user into the app

@app.route('/login',methods=['POST','GET'])
def login():
	if(request.method=='POST'):
		email=request.form['loginemail']
		password=request.form['loginPassword']
		

		
		userauth=auth.sign_in_with_email_and_password(email,password)
		cookie=userauth['idToken']
		session['user_id'] = cookie

		
		
		session['email'] = email

		


		temp = session.get('email')

		username=acc.get_user_name(temp)
		session['username']=username


		return redirect(url_for('Home'))

#------------------------------------------------------------------------------#

@login_required
@app.route('/explore/<int:page_no>')
def explore(page_no):

	
	
	return exp.render_page(session.get('email'),page_no)


#------------------------------------------------------------------------------#


@app.route('/signup_login',methods=['GET'])
def signup_login():
	return render_template('signup.html')

def check_email_exists(email):
	try:
		users = admin_auth.list_users().iterate_all()
		for user in users:
			if user.email == email:
				return True
	except Exception as e:
		return False

#------------------------------------------------------------------------------#
@app.route('/send_otp',methods=['GET','POST'])
def send_otp():
	response_data = {'message': 'Signup successful','email_exists':False}

	data=request.get_json()
		
	
	flag=check_email_exists(data['email'])
	

	if(flag==True):
		response_data['email_exists']=True
		return jsonify(response_data),404
	

	session['username']=data['username'].strip()
	session['email']=data['email'].strip()
	session['phone']=data['phone']
	session['friends_referal_id']=data['referal_id']

	if(data['password']==data['confirm_password']):

		session['password']=data['password']
		get_otp=generate_otp()
		response_data['otp']=str(get_otp)

		

		mail.send_otp(session['username'],session['email'],get_otp)
		
		return jsonify(response_data), 200

	response_data['message']='FAIL'

	return jsonify(response_data),404

  	
	 

@app.route('/signup',methods=['GET','POST'])
def signup():

	
	database=config.Setup_DataBase()

	friend_referal_id=session.get('friends_referal_id')

	data={
		'username':session.get('username'),
		'email':session.get('email'),
		'phone':session.get('phone'),
		'password':session.get('password'),
		'referal_id':contest.generate_random_string(10)
		
		}
	
	auth.create_user_with_email_and_password(data['email'],data['password'])

	


	database.child("Users").push(data)
	database.child(data['username']).push("")
	mail.sucess_registration(data['username'],data['email'])

	if(friend_referal_id!=''):
		acc.add_referal(friend_referal_id.strip())

	session['username']=''
	session['email']=''
	session['phone']=''
	session['password']=''
	session['friends_referal_id']=''

	response_data = {'message': 'Signup successful'}

	return jsonify(response_data), 200 


	

@app.route('/sucess_register')
def sucess_register():
	return render_template('success.html',data="THANKS FOR REGISTERING")


#------------------------------------------------------------------------------#

@app.route('/logout')
def logout():
    # Clear the user ID from the session
    session.pop('user_id', None)
    return redirect(url_for('Home'))
@app.route('/post_question',methods=['POST','GET'])
def post_question():
	if(request.method=='POST'):
		title=request.form['title']
		post=request.form['post']
	return forums.post_question(session.get('username'),title,post)

@app.route('/post_comments/<title>',methods=['POST','GET'])
def post_comments(title):
	if(request.method=='POST'):
		comment=request.form['commentContent']
	
	
	return forums.forum_post_comment(session.get('username'),title,comment)



@app.route('/forum')
def forum():
	forums_data=forums.forum_post_data()
	comment_data=forums.forum_comment_data()

	print(comment_data)

	

	return render_template('forum.html',data=forums_data,count=len(forums_data['Title']),comment_data=comment_data)

@app.route('/contact')
def contact():
	return render_template('Contact.html')

@app.route('/our_team')
def our_team():
	return render_template('our_team.html')

@app.route('/terms')
def terms():
	return render_template('Terms.html')
	
@app.route('/testimonials')
def testimonials():
	return render_template('testimonials.html')

@app.route('/about')
def about():
	return render_template('About.html')

@app.route('/FAQ')
def FAQ():
	return render_template('FAQ.html')

#------------------------------------------------------------------------------#

@app.route('/create_contest')
@login_required
def create_contest():
	
	return contest.render_page(session.get('username'))

#------------------------------------------------------------------------------#



'''
@app.route('/submit_contest',methods=['POST','GET'])
def submit_contest():
	contest=Create_Contest()
	if(request.method=='POST'):
		title=request.form['title']
		description=request.form['title']
		username=session.get('username')
		price=request.form['price']
		royalities=request.form['royalities']
		options=request.form['options']


	return contest.push_user_data(title,description,username,price,royalities,options,session.get('email'))
#------------------------------------------------------------------------------#
'''
@app.route('/account',methods=['GET','POST'])
@login_required
def account():
	view_email = request.args.get('view_email')
	view_username = request.args.get('view_username')

	if(view_email!=None and view_username!=None):

		return acc.render_page(view_email,view_username,False)

	
	return acc.render_page(session.get('email'),session.get('username'))

@app.route("/profile_picture",methods=['GET','POST'])
def profile_picture():
	
	file=request.files['profile_picture']

	

	return acc.update_profile_picture(file,session.get('email'),session.get('username'))

	
@app.route('/item_details/<contest_id>')
@login_required
def item_details(contest_id):
	return items.view_items_details(contest_id=contest_id,email=session.get('email'))


@app.route('/success')
@login_required
def success():
	return render_template('success.html',data="Your contest created successfully")

@app.route('/cancel')
@login_required
def cancel():
	return "OOPS"



#------------------------------------------------------------------------------#
@app.route('/upi_payment/<contest_id>/<Admin>')
def upi_payment(contest_id,Admin):
	data=exp.get_contest_data(session.get('email'),contest_id,"Contest",None)
	qr=qrcode.generate_qr_code(data)
	return render_template('upi_payment.html',url='success_join',qr=qr,title=data['title'][0],username=session.get('username'),Fee=data['price'][0],contest_id=contest_id,Admin=Admin)

@app.route('/bank_payment/<contest_id>/<Admin>')
def bank_payment(contest_id,Admin):
	data=exp.get_contest_data(session.get('email'),contest_id,"Contest",None)
	return redirect(payment.create_payment_stripe(data,False,False))
	

@app.route('/upi_pay_host',methods=['POST','GET'])
def upi_pay_host():
	data=request.get_json()
	price=int(data['price'])*82
	


	royalities=data['royalities']

	if((royalities.lower()).strip()=='yes'):
		referal_id=acc.get_referal_details(session.get('email'))
		balance=acc.update_referal_id(referal_id,False)

		if(balance>0):
			acc.update_referal_id(referal_id,True)
			price//=2

	data['ind_price']=str(price)

	data['title']=[data['title']]
	data['price']=[data['price']]
	
	
	qr=qrcode.generate_qr_code(data)
	message={
	'status':200,
	'qr':qr,
	'title':data['title'][0],
	'username':session.get('username'),
	'price':data['price'][0],
	'ind_price':str(price),
	'description':data['description'],
	'options':data['options'],
	'royalities':data['royalities']
	}
	session['message']=message
	#return render_template('upi_payment.html',qr=qr,title=data['title'][0],username=session.get('username'),Fee=data['price'][0])


	return jsonify(message), 200 

@app.route('/upi_gateway_host')
def upi_gateway_host():
	data=session.get('message')

	return render_template('upi_payment.html',url='success_host',qr=data['qr'],title=data['title'],username=session.get('username'),Fee=data['ind_price'])


@app.route('/success_host')
def success_host():
	data=session.get('message')
	session['message']=''

	contest=Create_Contest()

	title=data['title']
	description=data['description']
	price=data['price']
	royalities=data['royalities']
	username=session.get('username')
	options=data['options']

	return contest.push_user_data(title,description,username,price,royalities,options,session.get('email'))




@app.route('/bank_pay_host',methods=['POST','GET'])
def bank_pay_host():
	data=request.get_json()
	print(data)
	session['message']=data
	price=int(data['price'])

	royalities=data['royalities']

	if((royalities.lower()).strip()=='yes'):
		referal_id=acc.get_referal_details(session.get('email'))
		balance=acc.update_referal_id(referal_id,False)

		if(balance>0):
			acc.update_referal_id(referal_id,True)
			price//=2

	data_2={
	'title':data['title'],
	'price':price
	}

	pay=payment.create_payment_stripe(data_2,False,True)

	message={
	'status':200,
	'url':pay
	}
	print('hello')
	return jsonify(message),200
	






@app.route('/join_contest/<contest_id>/<Admin>')
@login_required
def join_contest(contest_id,Admin):

	'''
	'Payment to be Done here'
	'''
	
	
	

	#return redirect(url_for('success_join',contest_id=contest_id,Admin=Admin))

@app.route('/success_join/<contest_id>/<Admin>')
@login_required
def success_join(contest_id,Admin):
	print(contest_id,Admin)
	#chat.add_user(contest_id,session.get('email'),session.get('username'),Admin=(Admin))
	return render_template('success.html',data="Your have joined successfully")

@app.route('/mycontest')
def mycontest():
	return my_contest.show_contest(session.get('email'))

@app.route('/search_contest/<int:page_no>',methods=['GET','POST'])
def search_contest(page_no):
	if request.method=='POST':
		keyword=request.form['keyword']
		Category=request.form['Category']
		

		if Category=='All Categories':
			Category=None
		
		session['keyword']=keyword
		session['Category']=Category
		
	data={
		'title':session.get('keyword'),

		'options':session.get('Category')
		}
	

	return exp.search_page(session.get('email'),page_no,data)

	
	


@app.route('/message')
@login_required
def message():
	ids=chat.get_user_chat(session.get('email'))
	history_chat=chat.get_history_chat(ids)
	print(ids,"\n",history_chat)
	

	

	if(len(ids)==0):
		return render_template('404.html',error="No contest Hosted and No Contest Join",solution="Read the Help")
	session['current_contest_id']=ids[0]

	return chat.render_chat_page(history_chat,session.get('email'),ids,session.get('current_contest_id'),history_chat['title'][0],history_chat['URL'][0],False)

@app.route('/change_chat/<contest_id>')
@login_required
def change_chat(contest_id):
	ids=chat.get_user_chat(session.get('email'))
	history_chat=chat.get_history_chat(ids)
	session['current_contest_id']=contest_id

	index=ids.index(contest_id)
	title=history_chat['title'][index]
	url=history_chat['URL'][index]
	

	return chat.render_chat_page(history_chat,session.get('email'),ids,session.get('current_contest_id'),title,url,False)


@app.route('/Admin',methods=['POST','GET'])
def Admin():
	if(session.get('user_id')):
		return admin.home_page()
	if(request.method=='POST'):
		email=request.form['emailAdress']
		password=request.form['password']
		
		if(email=='raviajay9344@gmail.com' and password=='raviajay.2003'):
			session['username']="Admin"
			session['user_id']='admin_secrete_key'

			return admin.home_page()

	return admin.render_page()


@app.route('/Admin_Contest_Delete/<contest_id>')

def Admin_Contest_Delete(contest_id):
	admin.delete_contest(contest_id)

	redirect(url_for('Admin'))

@app.route("/admin_chat")
def admin_chat():
	contest_ids=admin.admin_chat_page()


	history_chat=chat.get_history_chat(contest_ids,True)

	session['current_contest_id']=contest_ids[0]
	

	return chat.render_chat_page(history_chat,None,contest_ids,session.get('current_contest_id'),history_chat['title'][0],history_chat['URL'][0],True)

@app.route("/change_admin_chat/<contest_id>")
def change_admin_chat(contest_id):
	contest_ids=admin.admin_chat_page()
	history_chat=chat.get_history_chat(contest_ids,True)


	session['current_contest_id']=contest_id

	index=contest_ids.index(contest_id)
	title=history_chat['title'][index]
	url=history_chat['URL'][index]

	return chat.render_chat_page(history_chat,None,contest_ids,session.get('current_contest_id'),title,url,True)

@app.route('/free_contest_create',methods=['POST','GET'])
def free_contest_create():
	if(request.method=='POST'):
		title=request.form['title']
		description=request.form['description']
		price=request.form['price']
		options=request.form['options']

		admin.create_contest(title,description,price,options)


	return admin.display_contest_page()

@app.route('/free_contest_details/<contest_id>')
def free_contest_details(contest_id):
	free_contest_data=admin.get_free_data(contest_id)

	return render_template('details.html',data=free_contest_data,contest_id=contest_id,Admin=True)

@app.route('/push_notifications/<username>',methods=['POST','GET'])
def push_notifications(username):

	notify=Notifications()
	if(request.method=='POST'):
		notification=request.form['notification']
		

		notify.push(notification,username)


	return notify.show_notifications_page()



@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    session['current_contest_id'] = room
    print("JOIN"+room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    print("LEAVE"+room)
    session.pop('current_contest_id', None)


@socketio.on('message')
def handle_message(message):

	param = message['url'].split('/')[-1]

	word=cyber.check_bad_words(message['message'])
	Bad_word=False
	room = session.get('current_contest_id')

	

	if(word==True):
		Bad_word=True
	else:
		database=client["Chats"]
		collection=database[session.get('current_contest_id')]
		data={
		'username':session.get('username'),
		'message':message['message'],
		'time':str(date_time)
		}
		collection.insert_one(data)
		

	
	emit('response', {'data': message['message'],'isYou':True,'time':str(date_time),'Bad_word':Bad_word},broadcast=True,room=room)
	

if __name__=="__main__":
	socketio.run(app,debug=True)
