import requests,re
from bs4 import BeautifulSoup
import lxml.html as parsingHTML
import MySQLdb
from datetime import datetime
from pprint import pprint


class getAllJobsFromDice():

	def __init__(self,keyword=None,state=None,portalid=2,keywordid=1,stateid=1):
	# MySQL connection is made to store data.
		self.db = MySQLdb.connect("localhost","root","","slack")
		self.cursor = self.db.cursor()
		self.status = True
		self.portalid = int(portalid)
		self.keywordid = int(keywordid)
		self.stateid  = int(stateid)
		# keyword = keyword.strip()
		# keyword = keyword.replace(" ","_")
		self.keyword = keyword
		self.state = state
		self.hitTheJob()

	def hitTheJob(self):
	# Finding all jobs that match the Keyword.
		getAllSQL = """SELECT * FROM jobs_keyword_search"""
		self.cursor.execute(getAllSQL)
		allKeywords = self.cursor.fetchall()
		for i in allKeywords:
			keywordid = i[0]
			keyword   = i[1]
			keyword = keyword.lower()
			denykeywordsID = i[3]
			self.denykeywordsIDGlobal = denykeywordsID
			slackid   = i[4]
			getAllStates = """SELECT * FROM jobs_allusstates"""
			self.cursor.execute(getAllStates)
			allStatesGet = self.cursor.fetchall()
			
			for city in allStatesGet:
	# Finding all jobs in US states
				stateid = city[0]
				statename = city[1]
				statekey = city[2]
				# print stateid,":",statename,":",statekey
				self.slackid = slackid
				self.keywordid, self.portalid,self.stateid = keywordid,self.portalid,self.stateid
				self.state,self.keyword = statename,keyword
				self.state = self.state.replace(" ","_")

				self.searchKeyword = keyword.replace(" ","_")

				self.getAllJobs()

	def getDenyKeywordsFromDb(self,denyID):
		getAllSQL = """ SELECT * FROM  jobs_denywordslist WHERE id = '{0}'""".format(denyID)
		self.cursor.execute(getAllSQL)
		allKeywords = self.cursor.fetchall()
		return allKeywords[0][1].split(',')

	def getAllJobs(self):
	# Finding all jobs from dice.com
		listOfPages = [1,2,3,4]
		for pageno in listOfPages:
			self.makeurl = """https://www.dice.com/jobs/q-{0}-jtype-Contracts+OR+Third Party-sort-relevance-limit-30-l-{1}-radius-30-startPage-{2}-limit-30-jobs""".format(self.searchKeyword,self.state,pageno)

			print self.makeurl
			# break
			respo = requests.get(self.makeurl)
			soup = BeautifulSoup(str(respo.content),"lxml")
			allevents = soup.findAll("div",{"class":"serp-result-content bold-highlight"})
			for ii in allevents:
				subSoup = BeautifulSoup(str(ii),"lxml")
				htmll = parsingHTML.fromstring(str(ii))

	# Variables used to store data under various headers.
				title = htmll.xpath("//h3/a/text()")
				title = self.listToStrAndParse(title)
				url = htmll.xpath("//h3/a/@href")[0]

				company = htmll.xpath("//ul//a/text()")[0]
				location = htmll.xpath("//ul/li[2]/text()")[0]
				description = htmll.xpath("//div[@class='shortdesc']/text()")
				description = self.listToStrAndParse(description)
				jobDict = {
						"title":title,
						"url":url,
						"company":company,
						"location":location,
						"description":description
						}
				# pprint(jobDict)
				self.getJobIntoDB(jobDict)


	def getJobIntoDB(self,jobDetails):
	# Storing the data fetched from website into database
		title =  self.cleanText(self.parseText(jobDetails['title'])) 
		url = jobDetails['url']
		company = self.cleanText(self.parseText(jobDetails['company'])) 
		location = self.cleanText(self.parseText(jobDetails['location'])) 
		description = self.cleanText(self.parseText(jobDetails['description'])) 

		title = title.encode('ascii','ignore')
		title = self.cleanText(self.parseText(title))
		title = title.replace("'","")
		title = title.replace("'","")
		title = title.replace("'","")

		testtitle = title.lower()



		print "COMPARING:::::::",self.keyword,">>>>>>>>>>>>>",testtitle
		if self.keyword in testtitle:
			keywordsToDenyInMail = self.getDenyKeywordsFromDb(self.denykeywordsIDGlobal)
			print "Keyword to deny in mail:::",keywordsToDenyInMail
			statusTosendContent = True
			for word in keywordsToDenyInMail:
				word = word.lower()
				if word in testtitle:
					statusTosendContent = False
					break

			if statusTosendContent == True:
				print "AVAAIBLE ::::::::::"
				pprint(jobDetails)
				body = description.encode('ascii', 'ignore')
				body = self.cleanText(self.parseText(body))
				body = body.replace("'","")
				body = body.replace("'","")
				body = body.replace("'","")

		# Preparing Slack Content
				slacksql = """SELECT * FROM jobs_slack_channel where id = '{0}' """.format(self.slackid)
				self.cursor.execute(slacksql)
				allslackresults = self.cursor.fetchall()

				prepareSlackContent = """ 
				Job Title: {0} \n Job Description: {1} \n Job Location: {2} \n Company: {3} \n Url: {4}
				{5}
				""".format(title,body,location,company,url,"_"*100)

				checksql = """ SELECT * FROM  jobs_job WHERE job_url = '{0}' """.format(url)
				self.cursor.execute(checksql)
				results = self.cursor.fetchall()
				if len(results) == 0:
					sql = """  INSERT INTO  jobs_job (job_title,job_discription,company_name,company_email,send_on_slack,last_updated,keyword_id,portal_id_id,job_url,state_id)
						VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')
					""".format(title,body,company,'',1,str(datetime.now()),self.keywordid,self.portalid,url,self.stateid)
					try:
						self.cursor.execute(sql)
						self.db.commit()
						try:
							for sl in allslackresults:
								self.sendPayloadToSlack(sl[1],prepareSlackContent,sl[2])
						except:
							print "ERROR IN SLACK SEND"
					except:
						print "ERROR IN INSERT............"
						self.db.rollback()
				else:
					pass

	def getDenyKeywordsFromDb(self,denyID):
		getAllSQL = """ SELECT * FROM  jobs_denywordslist WHERE id = '{0}'""".format(denyID)
		self.cursor.execute(getAllSQL)
		allKeywords = self.cursor.fetchall()
		try:
			return allKeywords[0][1].split(',')
		except:
			return []


			# This method is sending Messeges to Slack after filtering all the requioments
	def sendPayloadToSlack(self,channelname,content,hooksurl):
	# Sending message on to the slack.
		if "#" in channelname:pass
		else:channelname = "#{0}".format(channelname)
		data = {
				"channel": channelname,
				"username": self.keyword,
				"text": content,
				"icon_emoji": ":ghost:"
				}
		requests.post(hooksurl, json=data)
		print "SENT ON SLACK ",data
		print "HOOKS ",hooksurl


		# This method will just convert list into string and also filter the string with unwanted characters
	def listToStrAndParse(self,MyList):
	# Parsing the data on website and decoding it.
		dumm = ""
		for ele in MyList:
			ele = ele.encode('ascii', 'ignore').decode('ascii')
			dumm = "{0} {1}".format(dumm,self.cleanText(self.parseText(ele)))
		return dumm

	def parseText(self, str):
	# Parsing the data on website that is unwanted text.
		soup = BeautifulSoup(str, 'html.parser')
		return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()

	def cleanText(self,text):
	# Cleaning the data on website to remove unwanted text
		soup = BeautifulSoup(text,'html.parser')
		text = soup.get_text();
		text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
		return text 




if __name__ == '__main__':
	obj = getAllJobsFromDice()


