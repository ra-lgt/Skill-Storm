from flask import Flask,render_template,request,session,redirect,url_for,make_response,jsonify,send_file
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
import logging
from withdraw import Withdraw

# Initialize the Firebase Admin SDK


#All Files are imported

date_time=datetime.datetime.now()
cyber=Cyberbullying()
withdraw=Withdraw()
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
socketio = SocketIO(app,cors_allowed_origins="*")
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




# Configure error logging
app.config['PROPAGATE_EXCEPTIONS'] = True  # To propagate exceptions to log
app.config['DEBUG'] = False  # Set to True for development, False for production

# Define a log file and log level
log_filename = 'flask_error.log'
log_level = logging.ERROR  # Log only error and higher level messages

# Create a file handler for the log file
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(log_level)

# Create a log formatter
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the app's logger
app.logger.addHandler(file_handler)

@app.errorhandler(500)
def handle_500_error(error):
    return render_template('500.html',data="Reload the home page again or check your credentials or clear your cookieand try again"), 500

@app.route('/sitemap', methods=['GET'])
def sitemap():
	xml_file_path = 'sitemap.xml'
	return send_file(xml_file_path, mimetype='application/xml')

@app.errorhandler(502)
def handle_500_error(error):
    return render_template('500.html',data="Reload the home page again or check your credentials or clear your cookieand try again"), 500

def generate_otp():
	sequence_length = 5
	min_value = 10 ** (sequence_length - 1)  # Smallest 5-digit number (10000)
	max_value = (10 ** sequence_length) - 1  # Largest 5-digit number (99999)
	random_number = random.randint(min_value, max_value)
	return random_number

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',error=None,solution=None), 404


@app.route('/email_exists')
def email_exists():
	return render_template('404.html')

def login_required(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        
        
        if session.get('user_id'):
            return view_function(*args, **kwargs)
        else:
            return redirect(url_for('signup_login'))
    return decorated_function

@app.route('/.well-known/pki-validation/628C744FD49E8622CE9E2C92B902AF43.txt')
def ssl():
    return ("""E489EACFD181A584E561FFF2A52B33F664B929A64A53C27E02818B40C1B23A38
comodoca.com
abf0132d699b3fb""")

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
	
	
	
	return render_template('index.html',data=payload,notification=user_not,count=len(user_not['data']),free_contest=free_contest,free_count=len(free_contest['id']))

#------------------------------------------------------------------------------#

#login page which signin's the user into the app

@app.route('/login',methods=['POST','GET'])
def login():
	if(request.method=='POST'):
		email=request.form['loginemail']
		password=request.form['loginPassword']
		

		try:
			userauth=auth.sign_in_with_email_and_password(email,password)
		except:
			error_url = url_for('error', data="Invalid login", reason="Check your credentials and try again or contact us")

			return redirect(error_url)
		cookie=userauth['idToken']
		session['user_id'] = cookie

		
		
		session['email'] = email

		


		temp = session.get('email')

		username=acc.get_user_name(temp)
		session['username']=username


		return redirect(url_for('Home'))

#------------------------------------------------------------------------------#


@app.route('/explore/<int:page_no>')
@login_required
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
	withdraw.generate_user_register_balance(data['username'],data['email'])

	


	database.child("Users").push(data)
	database.child(data['username']).push("")
	mail.sucess_registration(data['username'],data['email'])

	if(friend_referal_id!=''):
		acc.add_referal(friend_referal_id.strip()) #Friends
		acc.add_referal(data['referal_id'].strip()) #Yours

	session['username']=''
	session['email']=''
	session['phone']=''
	session['password']=''
	session['friends_referal_id']=''

	response_data = {'message': 'Signup successful'}

	return jsonify(response_data), 200 


	

@app.route('/sucess_register')
def sucess_register():
	return render_template('success_join.html',data="THANKS FOR REGISTERING")


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
@login_required
def forum():
	forums_data=0
	comment_data=0
	try:
		forums_data=forums.forum_post_data()
		comment_data=forums.forum_comment_data()
	except:
		print()
	


	return render_template('forum.html',data=forums_data,count=len(forums_data['Title']),comment_data=comment_data)

@app.route('/get_started')
def get_started():
	return render_template('get_started.html')

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

@app.route('/contact_form',methods=['GET','POST'])
def contact_form():
	if(request.method=='POST'):
		username=request.form['username']
		email=request.form['email']
		message=request.form['message']

		db=client['Contact']
		collection=db['Users_query_details']

		collection.insert_one({
			'username':username,
			'email':email,
			'message':message,
			})

		return render_template('success_join.html',data="Will reach out to you")



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
	data['ind_price']=int(data['price'][0])*82
	
	qr=qrcode.generate_qr_code(data)

	if(session.get('username') in config.admin_creds['username'] and session.get('email') in config.admin_creds['email']):
		return redirect(url_for('success_join',contest_id=contest_id,Admin=False))

	return render_template('upi_payment.html',url='success_join',qr=qr,title=data['title'][0],username=session.get('username'),Fee=data['ind_price'],contest_id=contest_id,Admin=Admin)

@app.route('/bank_payment/<contest_id>/<Admin>')
def bank_payment(contest_id,Admin):
	data=exp.get_contest_data(session.get('email'),contest_id,"Contest",None)

	if(session.get('username')=='raviajay' and session.get('email')=='raviajay9344@gmail.com'):
		return redirect(url_for('success_join',contest_id=contest_id,Admin=False))
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
	'royalities':data['royalities'],
	'criteria':data['criteria']
	}
	session['message']=message
	#return render_template('upi_payment.html',qr=qr,title=data['title'][0],username=session.get('username'),Fee=data['price'][0])


	return jsonify(message), 200 

@app.route('/upi_gateway_host')
def upi_gateway_host():
	data=session.get('message')
	if(session.get('username')=='raviajay' and session.get('email')=='raviajay9344@gmail.com'):
		return redirect(url_for('success_host'))

	return render_template('upi_payment.html',url='success_host',qr=data['qr'],title=data['title'],username=session.get('username'),Fee=data['ind_price'])
@socketio.on_error()  # Handles all namespaces without an explicit error handler
def handle_error(e):
    print("An error occurred:", e)


@socketio.on('success_host',namespace='/')
def success_host(data):
	
	emit('notify',data,namespace="/",broadcast=True)



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
	criteria =data['criteria']

	#socketio.emit('success_host', {'title':title,'price':price,'username':username,'description':description})


	return contest.push_user_data(title,description,username,price,royalities,options,criteria,session.get('email'))




@app.route('/bank_pay_host',methods=['POST','GET'])
def bank_pay_host():
	data=request.get_json()
	
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
	
	
	return jsonify(message),200
	



@app.route('/winner/<price>/<username>/<contest_id>')
@login_required
def winner(price,username,contest_id):
	withdraw.winner_add_balance(username,price,contest_id)
	return price	

@app.route('/withdraw_money')
@login_required
def withdraw_money():
	return withdraw.render_page(session.get('username'),session.get('email'))

@app.route('/make_withdraw/<Type>',methods=['POST','GET'])
@login_required
def make_withdraw(Type):
	withdraw_result=False

	if(request.method=='POST'):
		if(Type=='paypal'):
			email=request.form['email']
			amount=request.form['amount']
			withdraw_result=withdraw.withdraw_users_balance(session.get('email'),Type,{"paypal_email":email,"amount":amount})

		elif(Type=='upi'):
			amount=request.form['amount']
			upi_id=request.form['upi_id']
			withdraw_result= withdraw.withdraw_users_balance(session.get('email'),Type,{"upi_id":upi_id,"amount":amount})

		elif(Type=='bank'):
			acc_number=request.form['acc_number']
			ifsc_number=request.form['ifsc_number']
			recieptant_name=request.form['recieptant_name']
			amount=request.form['amount']
			withdraw_result= withdraw.withdraw_users_balance(session.get('email'),Type,{"acc_number":acc_number,"ifsc_number":ifsc_number,"recieptant_name":recieptant_name,"amount":amount})

	if(withdraw_result==False):
			error_url = url_for('error', data="Your balance is low", reason="Withdraw amount range should be within your balance")
			return redirect(error_url)
	return render_template('success_join.html',data="Withdraw successful")

@app.route('/error')
def error():
	data = request.args.get('data')
	reason = request.args.get('reason')

	return render_template('error.html',data={"data":data,"reason":reason})

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
	
	chat.add_user(contest_id,session.get('email'),session.get('username'),Admin=(Admin))
	return render_template('success_join.html',data="Your have joined successfully")


@app.route('/mycontest')
@login_required
def mycontest():
	return my_contest.show_contest(session.get('email'))


@app.route('/search_contest/<int:page_no>',methods=['GET','POST'])
@login_required
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
	
	if(request.method=='POST'):
		email=request.form['emailAdress']
		password=request.form['password']
		
		if(email=='raviajay9344@gmail.com' and password=='raviajay.2003'):
			session['username']="Admin"
			session['user_id']='admin_secrete_key'

			return admin.home_page()

	return admin.render_page()


@app.route('/Admin_Contest_Delete/<contest_id>/<Type>')

def Admin_Contest_Delete(contest_id,Type):
	if(Type=='Hosted'):
		Type="Contest"
	admin.delete_contest(contest_id,Type)

	return redirect(url_for('Admin'))

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
@login_required
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
    

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    
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
	socketio.run(app,debug=False)

