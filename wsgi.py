#!/bin/python
##########################################################
#This is a Flask RESTful wrapper
#To expose the
#
##########################################################
import re
import os
import requests
#import getpass
#import csv
#import cStringIO
from lxml import html
from flask import Flask,request,jsonify
import traceback
import logging
import hashlib

application = Flask(__name__)
#application.run(host="173.236.138.191")

def verifyEmail(email):


	session = requests.Session()
	r = session.get('https://www.wellnessliving.com/selfsignup/37RrPjmtY', timeout=5)

	tree=html.fromstring(r.text.replace('\\',''))

	controller=tree.xpath("//script[contains(.,'Ajax._startup')]/text()")
	ajaxID=str(controller[0]).split("'")[1]

	emailData={'a-ajax':ajaxID
             ,'a_data[id_place]':'4'
             ,'a_data[s_mail]':email
             ,'a_data[uid_current]':0
             ,'a_data[s_secret]':'37RrPjmtY'
             ,'s_method':'Wl\Login\Add\Ajax::mailVerifyPrompt'
	     }

	r=session.post("https://www.wellnessliving.com/a/ajax.html",data=emailData,timeout=10)

	return r.text


def createUser(fname,lname,email,pwd,phone,phoneHome,phoneWork,month,day,year,gender,address,city,postal,location,signature,city_code=27495):

	try:

		session = requests.Session()
		r = session.get('https://www.wellnessliving.com/Wl/Selfsignup.html?a-ajax=1&id_page=1&s_secret=37RrPjmtY&uid=0&a-ajax=1&_=1516447931224',timeout=15)

		tree=html.fromstring(r.text.replace('\\',''))

		postURL=tree.xpath('//form/@action')
		controller=tree.xpath('//input[@name="wl-selfsignup-controller"]/@value')

		userData={'wl-selfsignup-controller':controller[0]
	         ,'s_secret':'37RrPjmtY'
	         ,'a_image_upload[PassportLoginImage-new]':''
        	 ,'is_more':1
	         ,'s_firstname':fname
        	 ,'s_lastname':lname
	         ,'a_user[not_virtual]':1
        	 ,'a_user[s_mail]':email
	         ,'a_user[is_password_new]':1
        	 ,'a_user[s_password]':pwd
	         ,'a_user[s_password2]':pwd
        	 ,'s_phone':phone
	         ,'s_phone_home':phoneHome
        	 ,'s_phone_work':phoneWork
	         ,'i_month':month
        	 ,'i_day':day
	         ,'i_year':year
        	 ,'id_gender':int(gender)
	         ,'is_address_inherit':''
        	 ,'s_address':address
	         ,'s_city_custom':city
        	 ,'k_city':city_code  #27495 #code returned by the city search plugin?
	         ,'s_postal':postal
        	 ,'k_location':location #208833 #sterling v alexandria??
	         ,'s_search':''
        	 ,'uid_referrer':0
	         ,'a-ajax':1
        	 }
		#print(userData)
		r = session.post(postURL[0], data=userData,timeout=45)
	#application.logger.error( r.text )
	#extract response data including affirmation data
		try:

			tree=html.fromstring(r.text.replace('\\',''))

			if "\"s_status\":\"post-error\"" in r.text:
				raise Exception("An error occured while creating the User")

			postURL=tree.xpath('//form/@action')
			controller=tree.xpath('//input[@name="wl-selfsignup-controller"]/@value')

			#print (r.text)

			affirmData={'wl-selfsignup-controller':controller[0]
        		   ,'is_agree':1
	        	   ,'s_signature':signature
			   ,'a-ajax':1
			   }

		except:

			#application.logger.error( "Error parsing add user request")
			#application.logger.error(r.text)
			raise

		r = session.post(postURL[0],data=affirmData,timeout=45)

#	print r.text
		return r.text

	except Exception as e:
		print ("An Error occurred while creating the account")
		print (r.text)
		return jsonify({"error": "An Error occurred creating the account: " + str(e)})
	finally:

		session.close()


def addMember(fname,lname,email,pwd,phone,phoneHome,phoneWork,month,day,year,gender,address,city,postal,location,signature,city_code=27495, attempt=1):

	try:

		session = userlogin(pwd,email)

		#print(session)
		addProfileURL='https://www.wellnessliving.com/rs/profile-edit.html?uid_from='+session["uid"]

	#Add Profile:
	#Request:
		#print(session["session"].get(addProfileURL))
		r = session["session"].get(addProfileURL)

		#print ("Click add profile")
		#print (r.text)

		tree=html.fromstring(r.text.replace('\\',''))
		postURL=tree.xpath('//form/@action')
		controller=tree.xpath('//input[@name="rs-profile-edit"]/@value')

	#Edit Profile:
		addData =   {"rs-profile-edit":controller[0]
        	    ,"a_pay[uid]":0
	            ,"a_family_relation[0][id_family_relation]":5
        	    ,"a_family_relation[0][uid_to]":session["uid"]
	            ,"a_image_upload[PassportLoginImage-new]":""
        	    ,"is_more":1
	            ,"s_firstname":fname
        	    ,"s_lastname":lname
	            ,"a_user[is_mail_inherit]":"on"
        	    ,"a_user[is_password_new]":1
	            ,"s_phone":phone
        	    ,"s_phone_home":phoneHome
	            ,"s_phone_work":phoneWork
        	    ,"i_month":month
	            ,"i_day":day
        	    ,"i_year":year
	            ,"id_gender":gender
        	    ,"s_address":address
	            ,"s_city_custom":city
	            ,"k_city":city_code#27495 #???where does this number come from?
        	    ,"s_postal":postal
	            ,"k_location":location #208833 #sterling??
        	    ,"s_search":''
	            ,"uid_referrer":0
        	    }

		#print("Child Data:")
		#print(addData)
		#print(postURL)

		r = session["session"].post(postURL[0],data=addData)

		#print (r.text)
		tree=html.fromstring(r.text.replace('\\',''))
		links=tree.xpath("//a[contains(@href,'relative-login') and contains(@title,'"+fname+"')]/@href")

		signInURL=links[0]
		addedUID=str(links[0]).split("=")[-1]

	#Sign Waiver:

	#"sign in" as the added user
		r = session["session"].get(signInURL)

#	print r.text
	#now get the waiver form for the new user
		r = session["session"].get('https://www.wellnessliving.com/rs/login-agree.html', timeout=30)

#	print r.text
		try:
			tree=html.fromstring(r.text.replace('\\',''))

			postURL='https://www.wellnessliving.com/a/ajax.html'

			controller=tree.xpath("//script[contains(.,'Ajax._startup')]/text()")
			ajaxID=str(controller[0]).split("'")[1]

			affirmData={'a-ajax':ajaxID
        		   ,'a_data[is_catalog_register]':0
	        	   ,'a_data[k_business]':78906 #urbanevo number?
	        	   ,'a_data[s_signature]':signature
		   	   ,'s_method':'RsLogin::agreeBusiness'
	        	   }

		except:

			print ("Error parsing add child request")
			print (r.text)
			raise

		r = session["session"].post(postURL,data=affirmData,timeout=60)

#	print r.text
		return r.text

	except Exception as e:
		print("An error occurred while adding a child on attempt {}".format(attempt))
		if attempt <= 10:
			print("Retry creating child {} {} for {}".format(fname,lname,email))
			return addMember(fname,lname,email,pwd,phone,phoneHome,phoneWork,month,day,year,gender,address,city,postal,location,signature,city_code=27495, attempt=attempt+1)
		print("Final attempt to create child failed")
		return jsonify({"error": "Error creating child: "+str(e)})

@application.route("/city/<string:cityName>")
def getCities(cityName):
    cityName.replace('_', ' ')
    session = requests.Session()
    webdata = session.get('https://www.wellnessliving.com/a/combobox.html?a-ajax=1&s_id=city&s_name=k_city&s_unit=a.geo&s_value=' + cityName + '&a-ajax=1', timeout=15)
    longString = webdata.text
    cityDict = {}


    cityArray = longString.split("ac-span-item-city-")
    del cityArray[0]
    for item in cityArray:
        itemArray = re.split("<|>", item)
        cityDict[itemArray[1]] = itemArray[7]

    return jsonify(cityDict)

@application.route('/')
def hello_world():
	return register()

@application.route('/emailCheck/<string:email>')
def checkEmail(email):

	return verifyEmail(email)

@application.route('/help')
def help():
    helpData={"/help":"Returns Information on Operations"
            ,"/sample":"Returns sample JSON for the /createAccount method"
            ,"/createAccount":"Post JSON data to create the new user account"
            ,"/city/{name}":"Get query to lookup city codes.  Example /city/tuc"
            }
    return jsonify(helpData)

@application.route('/sample')
def sample():
	#Return sample input
#	return 'Help Coming Soon!'
	sample ={'fname':'Lazarus'
		,'lname':'Long'
		,'email':'adorable@dora.com'
		,'pwd':'methuselah'
		,'phone':'111-222-3333'
		,'phoneHome':'222-333-4444'
		,'phoneWork':'333-444-5555'
		,'month':'11'
		,'day':'11'
		,'year':'1911'
		,'gender':1 #need to track down the wellness lov values
		,'address':'1234 Fake Street'
		,'city':'Kansas City, MO, USA'
                ,'city_code':27495
		,'postal':'12345'
		,'location':'208833'
		,'members':[{'fname':'Lorelei'
			    ,'lname':'Long'
			    ,'gender':2
			    ,'month':7
			    ,'day':15
			    ,'year':2005
			    }
                           ,{'fname':'Lapus Lazuli'
                            ,'lname':'Long'
                            ,'gender':2
                            ,'month':7
                            ,'day':15
                            ,'year':2005
                            }
			   ]
		,'signature':'data:image/png;base64,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'
		}
	return jsonify(sample)


def formatPhone(phone):

	if phone != "":

		reg=re.compile('\D')
		phone=reg.sub('',phone)
		phone=phone[0:3]+"-"+phone[3:6]+"-"+phone[6:]

	#print(phone)
	return phone


@application.route('/createAccount',methods=['POST'])
def createAccount():

	try:
		content = request.get_json(force=True)
		print ("Registering " + content["email"])
		#print content["parent"]["fname"]


		phone=formatPhone(content["phone"])
		phoneHome=formatPhone(content["phoneHome"])
		phoneWork=formatPhone(content["phoneWork"])

		print(phone,phoneHome,phoneWork)


		checkEmail=verifyEmail(content["email"])

		#print(checkEmail)

		if "s_message" in checkEmail or "already" in checkEmail:

			return jsonify({"error":"Email Address Already Registered"})

		else:

			userResult=createUser(content["fname"],content["lname"],content["email"],content["pwd"],phone,phoneHome,phoneWork,content["month"],content["day"],content["year"],content["gender"],content["address"],content["city"],content["postal"],content["location"],content["signature"],content["city_code"])

			print("User Added " + content["email"])

	#		print(userResult)

			memberResult=[]

			for member in content["members"]:

			#	print member

				memberResult=memberResult+[addMember(member["fname"],member["lname"],content["email"],content["pwd"],phone,phoneHome,phoneWork,member["month"],member["day"],member["year"],member["gender"],content["address"],content["city"],content["postal"],content["location"],content["signature"],content["city_code"])]

				print ("Child Added " + member["fname"])

			return jsonify({"UserResult":userResult,"DependentResults":memberResult})

	except Exception as e:

		#traceback.print_stack()

		return jsonify({"error":str(e)})



@application.route('/register')
def register():
	return application.send_static_file('UrbanEvo.html')

#@application.route('/testlogin')
def userlogin(password, email):

	#password="thispasswordsucks"
	#email='a.aaaaaa@bbb.ccc'
	#start a session by pulling up the login page
	session = requests.Session()
	r = session.get('https://www.wellnessliving.com/login/urbanevo',timeout=30)

	#need to get the csrf from the reply
	#"a_form_csrf['core-request-api']='0TC8QbYNvdCYYOTj-VVnPqhcQwD8'"
	csrfPos = [m.start() for m in re.finditer("a_form_csrf\[\'core-request-api\'\]\=\'", r.text)]
	#print(len("a_form_csrf['core-request-api']='0TC8QbYNvdCYYOTj-VVnPqhcQwD8';"))
	#print(len("a_form_csrf['core-request-api']='0TC8QbYNvdCYYOTj-VVnPqhcQwD8';"))
	#print(csrfPos)
	#print(r.text[csrfPos[0]:csrfPos[0]+63])
	csrf=r.text[csrfPos[0]:csrfPos[0]+63][33:61]
	#print(csrf)

	#retrieve a salt from the salt service
	#notepadPost={"s_login":email,"s_type":"","csrf":"0TC8QbYNvdCYYOTj-VVnPqhcQwD8","_":"1538843048758"}
	notepad=session.get('https://www.wellnessliving.com/Core/Passport/Login/Enter/Notepad.json?s_login='+email+'&s_type=&csrf=' + csrf + '&_=1538843048758')
	notepadData=notepad.json()
	#print(notepadData)
	#print(notepadData["s_notepad"])
	salt=notepadData["s_notepad"]

	#this is a copy from the wellness js that handles the "passport" processself.
	#i believe this is the hashing mechanism used on the server side to store password
	s_hash=''
	delim=['r','4S','zqX','zqiOK','TLVS75V','Ue5aLaIIG75','uODJYM2JsCX4G','kt58wZfHHGQkHW4QN','Lh9Fl5989crMU4E7P6E']
	for a in delim:
		s_hash=s_hash+a+password

	firstHash= salt + hashlib.sha3_512(s_hash.encode('utf-8')).hexdigest()

	secondHash=hashlib.sha3_512(firstHash.encode('utf-8')).hexdigest()

	loginData={'i':0
	  ,'s_password':secondHash
	  ,'s_login': email
	  ,'s_notepad':notepadData["s_notepad"]
	  ,'s_captcha':''
	  ,'csrf':csrf
	  }

	loginResponse=session.post("https://www.wellnessliving.com/Core/Passport/Login/Enter/Enter.json",data=loginData)
	#print(loginResponse.json())
	#print ("After Logon")

	#need to get the UiD
	userInfoGet=session.get("https://www.wellnessliving.com/Core/Passport/Login/Info.json?csrf="+csrf+"&_=1538843048759")
	userInfo=userInfoGet.json()
	#print(userInfo)
	#print(userInfo["uid"])
	#getuserinfo=session.get("https://www.wellnessliving.com//rs/schedule/urbanevo?k_class_tab=2868&uid=12314053&id_class_tab=1")
	return {"session":session,"uid":userInfo["uid"],"csrf":csrf}

if __name__ == "__main__":

	#gunicorn_logger = logging.getLogger('gunicorn.error')
	#application.logger.handlers = gunicorn_logger.handlers
	application.run(debug=True,host='0.0.0.0', port=8080)
	#application.run()
