import requests,re
from bs4 import BeautifulSoup
import lxml.html as parsingHTML
import MySQLdb
from datetime import datetime
from pprint import pprint


class getAllJobsFromIndeed():

	def __init__(self,keyword=None,state=None,portalid=1,keywordid=1,stateid=1):
	# creating a MySQL database
		self.db = MySQLdb.connect("localhost","root","","slackapp")
		self.cursor = self.db.cursor()
		self.status = True
		self.portalid = int(portalid)
		self.keywordid = int(keywordid)
		self.stateid  = int(stateid)
		keyword = keyword.strip()
		keyword = keyword.replace(" ","+")
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
			slackid   = i[4]
				
			denykeywordsID = i[3]
			self.denykeywordsIDGlobal = denykeywordsID

			getAllStates = """SELECT * FROM jobs_allusstates"""
		# Finding all jobs in US states
			self.cursor.execute(getAllStates)
			allStatesGet = self.cursor.fetchall()
			for city in allStatesGet:
				stateid = city[0]
				statename = city[1]
				statekey = city[2]
				# print stateid,":",statename,":",statekey
				self.slackid = slackid
				self.keywordid, self.portalid,self.stateid = self.keywordid,1,self.stateid
				self.state,self.keyword = statename,keyword
				self.getAllJobs()



			# self.state = 

			# print keywordid,"::",keyword,"::",slackid





	def getAllJobs(self):
	# Finding all jobs from indeed.com
		# listpages = [0,10,20]
		# for pageno in listpages:
		# self.makeurl = """https://www.indeed.com/jobs?q={0}&l={1}&start={2}&pp=""".format(self.keyword,self.state,pageno)
		self.makeurl = """https://www.indeed.com/jobs?as_and=&l={0}&as_phr=&as_any=&as_not=&as_ttl={1}&as_cmp=&jt=contract&st=&salary=&radius=25&fromage=any&limit=40&sort=date&psf=advsrch""".format(self.state,self.keyword)
		print self.makeurl
		respo = requests.get(self.makeurl)
		soup = BeautifulSoup(str(respo.content),"lxml")
		allevents = soup.findAll("div",{"data-tn-component":"organicJob"})
		for ii in allevents:
			subSoup = BeautifulSoup(str(ii),"lxml")
			htmll = parsingHTML.fromstring(str(ii))
			anchorcontent = subSoup.find('a',{"class":"turnstileLink"})
			
	# Variables used to store data under various headers.		
			title =  anchorcontent.get("title")
			url = anchorcontent.get('href')
			try:
				company = subSoup.find('span',{"class":"company"}).text
				company = self.cleanText(self.parseText(company))
			except:
				company = ''
			location = subSoup.find('span',{"itemprop":"addressLocality"}).text
			location = self.cleanText(self.parseText(location))
			description = subSoup.find('span',{"itemprop":"description"}).text
			description = self.cleanText(self.parseText(description))

			nextpage = htmll.xpath("//span[@class='np']/../../@href")
			url = "https://www.indeed.com{0}".format(url)
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

		if self.keyword in title:


			keywordsToDenyInMail = self.getDenyKeywordsFromDb(self.denykeywordsIDGlobal)
			print "Keyword to deny in mail:::",keywordsToDenyInMail

			statusTosendContent = True
			for word in keywordsToDenyInMail:
				word = word.lower()
				if word in title:
					statusTosendContent = False
					break
			print jobDetails

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
	obj = getAllJobsFromIndeed('php developer','Florida')
	# obj.getAllJobs()


