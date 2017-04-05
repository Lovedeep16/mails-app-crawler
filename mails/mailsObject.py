import datetime, email, imaplib, mailbox, os
import MySQLdb
from bs4 import BeautifulSoup
import re, requests
from pprint import pprint

detach_dir = '.'
class getMailsReport(object):

	def __init__(self,EMAIL_ACCOUNT=None,PASSWORD=None):
		self.EMAIL_ACCOUNT = EMAIL_ACCOUNT
		self.PASSWORD = PASSWORD
		self.db = MySQLdb.connect("localhost","root","","slack")
		self.cursor = self.db.cursor()
		self.get_all_mails()

	def get_all_mails(self):  
		# Method will fetch all mails from the account     
		checksql = """ SELECT * FROM mails_mail_id """
		self.cursor.execute(checksql)
		results = self.cursor.fetchall()
		for reso in results:
			self.MAILUNIID = int(reso[0])
			email = reso[1]
			password = reso[2]
			try:
				self.get_all(email,password)
			except Exception as e:
				print "ERROR IS::",e
				print "EMAIL::",email
				pass


	def get_all(self,EMAIL_ACCOUNT=None,PASSWORD=None,keywordToSearch='PHP'):
		# keywordd = raw_input('Enter the keyword::')
		keywordd = keywordToSearch
		keyword=(keywordd.lower())

		mail = imaplib.IMAP4_SSL('mail.privateemail.com')
		print "LOGINNNN ING>>>"
		mail.login(EMAIL_ACCOUNT, PASSWORD)
		mail.list()
		mail.select('inbox')
		result, data = mail.uid('search', None, 'ALL') # (ALL/UNSEEN)
		i = len(data[0].split())

		
		for x in range(i):
			print "IN THE PAGE LOOP"
			latest_email_uid = data[0].split()[x]
			result, email_data = mail.uid('fetch', latest_email_uid, '(RFC822)')
			# print email_data
			uuuid = email_data[0][0].split(" ")[0]
			uuid_key = email_data[0][0].split(" ")[-1].replace("{","").replace("}","")
			# print uuuid,":::::",uuid_key

			raw_email = email_data[0][1]
			raw_email_string = raw_email.decode('utf-8')
			raw_email_string = raw_email_string.encode("utf-8")
			self.email_message = email.message_from_string(raw_email_string)

			date_tuple = email.utils.parsedate_tz(self.email_message['Date'])
			if date_tuple:
					local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
					local_message_date = "%s" %(str(local_date.strftime("%a, %d %b %Y %H:%M:%S")))
					# print local_message_date
			else:
				local_message_date = ''

	# Data of every single mail is stored into headers.			
			email_from = str(email.header.make_header(email.header.decode_header(self.email_message['From'])))
			# print "FROM::"+email_from
			
			email_to = str(email.header.make_header(email.header.decode_header(self.email_message['To'])))
			
			subjectt = str(email.header.make_header(email.header.decode_header(self.email_message['Subject'])))
			subject=(subjectt.lower())
			# print"SUBJECT::"+subject
			
			for part in self.email_message.walk():
					if part.get_content_type() == "text/plain":
							bodyy = part.get_payload(decode=True)
							body=(bodyy.lower())
			# print "BODY::"+body
			body  = body.replace("\n","")
			body = body.replace("\r","")
			
	# A dictionary is created to store each email information.		
			maildictToInsert = {
					"mailuuid":uuuid,
					"mailuuid_key":uuid_key,
					"datetime":local_message_date,
					"from":email_from,
					"subject":subject,
					"body":body
			}
			getAllSQL = """SELECT * FROM jobs_keyword_search  """
			self.cursor.execute(getAllSQL)
			allKeywords = self.cursor.fetchall()
			for i in allKeywords:
				keywordid = i[0]
				keyword   = i[1]
				denykeywordsID = i[3]
				slackid   = i[4]
				keyword = keyword.lower()
				keywordsToDenyInMail = self.getDenyKeywordsFromDb(denykeywordsID)
				print "Keyword to deny in mail:::",keywordsToDenyInMail
				print "CHECKINNGGGGG",":::::",keyword,"::::::::::",subject,"::: SLaclid",slackid
				if keyword in subject:
				# A notification is send to slack via SLACK-ID
					statusTosendContent = True
					for word in keywordsToDenyInMail:
						word = word.lower()
						if word in subject:
							statusTosendContent = False
							break
					if statusTosendContent == True:
						self.slackid = slackid
						pprint(maildictToInsert)
						self.keywordToSearch  = keyword
						self.insertMailToDB(maildictToInsert)
					else:
						print "DENY MAILS::::::",":"*100
						pprint(maildictToInsert)
						print "DENY MAILS::::::",":"*100


	
	def getDenyKeywordsFromDb(self,denyID):
		getAllSQL = """ SELECT * FROM  jobs_denywordslist WHERE id = '{0}'""".format(denyID)
		self.cursor.execute(getAllSQL)
		allKeywords = self.cursor.fetchall()
		return allKeywords[0][1].split(',')


	def insertMailToDB(self,maildict):
	# Data is stored heare into the database under various headers.
		mailuuid 	 = maildict["mailuuid"]
		mailuuid_key = maildict["mailuuid_key"]
		datetimes 	 = maildict["datetime"]
		frommail     = maildict["from"]
		subject      = maildict["subject"]
		body         = maildict["body"]

	# body = body.encode('ascii', 'ignore')
		body = unicode(body, "utf-8", errors="ignore")
		body = body.encode('ascii', 'ignore')
		body = self.cleanText(self.parseText(body))
		body = body.replace("'","")
		body = body.replace("'","")
		body = body.replace("'","")
		body = body.replace("'","")
		body = body.replace("'","")
		body = body.encode('ascii', 'ignore')

		print "DATA TIMES::::::",datetimes

		mydate = datetimes.split(",")[1].split(":")[0].strip().split(" ")
		mydate = "{0} {1} {2}".format(mydate[0],mydate[1],mydate[2])

		old = datetime.datetime.strptime(mydate,'%d %b %Y')
		new = datetime.datetime.now()

		getdays = new - old

# If mail is older then 7 days i.e one week then it is discarded.
		gap = int(getdays.days)
		if gap < 7:
			slacksql = """SELECT * FROM jobs_slack_channel where id = '{0}' """.format(self.slackid)
			self.cursor.execute(slacksql)
			allslackresults = self.cursor.fetchall()


# Preparing Slack Content Message.
			prepareSlackContent = """ 

			New Job Email: {0} \n Date Time : {1} \n Subject : {2} \n Content : {3} \n
			{4}
			""".format(frommail,datetimes,subject,body,"_"*100)


			checksql = """ SELECT * FROM  mails_all_mails WHERE mail_UID = '{0}' and  mail_to_id = '{1}' """.format(mailuuid,self.MAILUNIID)
			self.cursor.execute(checksql)
			results = self.cursor.fetchall()
			if len(results) == 0:
				try:
					sql = """  INSERT INTO  mails_all_mails (mail_UID,mail_KEY,mail_from,mail_title,mail_discription,date_recieved,sync_time,last_updated,mail_to_id,status)
						VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')
					""".format(mailuuid,mailuuid_key,frommail,subject,body,datetimes,str(datetime.datetime.now()),str(datetime.datetime.now()),self.MAILUNIID,'1')
					print sql
					try:
						self.cursor.execute(sql)
						self.db.commit()
						try:
							for sl in allslackresults:
								channeltype = sl[3]
								if channeltype == 'mail':
									self.sendPayloadToSlack(sl[1],prepareSlackContent,sl[2])
								else:
									print "*"*100
									print channeltype
									print "*"*100
						except Exception as eee:
							print "ERROR IN SLACK SEND:::",eee
					except Exception as ee:
						print "ERROR IN INSERT>>>>>>",ee
						self.db.rollback()
						
				except:
					print "ERROR IN SQL"
					pass
			else:
				pass
		else:
			print "*"*100
			print "EMAIL IS OLDER THAN 7 Days"
			print "*"*100

		return True

	def sendPayloadToSlack(self,channelname,content,hooksurl):
	# Sending message on Slack on the basis of channel name and Username
		if "#" in channelname:pass
		else:channelname = "#{0}".format(channelname)
		data = {
				"channel": channelname,
				"username": self.keywordToSearch,
				"text": content,
				"icon_emoji": ":ghost:"
				}
		requests.post(hooksurl, json=data)
		print "SENT ON SLACK ",data
		print "HOOKS ",hooksurl


	def parseText(self, str):
	# Parsing the email to find unwanted text.
		soup = BeautifulSoup(str, 'html.parser')
		return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()

	def cleanText(self,text):
	# Cleaning the email to remove unwanted text.
		soup = BeautifulSoup(text,'html.parser')
		text = soup.get_text();
		text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
		return text 
						
	# def get_selected(self,subject,body,keyword):
	# 	if keyword in subject or keyword in body:
	# 		return True	
	# 	else:
	# 		return False

	# def get_attachments(self):		
	# 	for part in self.email_message.walk():
	# 		if part.get_content_maintype() == 'multipart': 
	# 				continue
	# 		if part.get('Content-Disposition') is None: 
	# 				continue

	# 		filename = part.get_filename()
	# 		counter = 1
		
	# 		if not filename:
	# 			filename = 'part-%03d%s' % (counter, 'bin')
	# 			counter += 1

	# 		att_path = os.path.join(detach_dir, filename)
			 
	# 		if not os.path.isfile(att_path) :
	# 			fp = open(att_path, 'wb')              
	# 			fp.write(part.get_payload(decode=True))
	# 			fp.close()

if __name__ == '__main__':
		obj=getMailsReport()  


									
