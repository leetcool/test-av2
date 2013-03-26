import os
import sys
import smtplib
import datetime

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from ..web.models import Report as DBReport

class Report:
	def __init__(self, results=None):
		self.results = results
		
		if results != None:
			self.report = self._prepare_report()
		else:
			self.report = None


	def _prepare_report(self):
		r = ""
		for l in self.results:
			if l is list:
				for el in l:
					print "  %s\n" % el
					r+= "  %s\n" % el
			else:
				print "%s\n" % l
				r+= "%s\n" % l
		return r

	def save_file(self, filename):
		if self.report is None:
			print "[report:savefile] Report can't be None"
			return False
		try:
			print "[*] RESULTS: \n%s" % self.report 

			# ordered = {}
			with open( filename, "wb") as f:
				f.write("REPORT\n")
				f.write(self.report)
		except Exception as e:
			print "[report:save_file] Impossible save file. Exception: %s" % e
			return False

	def _parse_results(self,filename):

		success = []
		errors  = []
		failed  = []

		with open(filename, 'rb') as f:
			
			for l in f.readlines():
				try:
					e=eval(l)
					for k in e:
						j = k.split(",")
						print j

						if "SUCCESS" in j[3] or "FAILED" in j[3]:
							print j[0],j[1],j[3].split(":")[2][3:-2].replace("+","")
							#j[0],j[1],j[3]
							res = {}
							
							res['av'] = j[0]
							res['kind'] = j[1]
							'''
							res['av'] = j[1]
							res['kind'] = j[0]
							'''
							res['result'] = j[3].split(":")[2][3:-2].replace("+","")

							if "SUCCESS" in j[3]:
								success.append(res)
								print len(success)
							else:
								failed.append(res)
								print len(failed)
				except:
					if "ERROR" in l:
						errors.append(l)
						print len(errors)
					#print "failed: %s" % e
					pass
		return success,errors,failed

	def _add_header(self, name):
		
		html_table_open = '''
		<table border=1 cellpadding=1 cellspacing=2 width=70%>
			<tr><td with=15%>Virtual Machine</td>
				<td with=15%>Kind of test</td>
				<td width=50%>Result</td>
				<td width=10%>TXT Report</td>
				<td width=10%>Screenshot</td></tr>
		'''		

		html_head  = "<h2>%s</h2>" % name
		html_head += html_table_open
		return html_head

	def _add_results(self, res):

		html_section = '''
		<tr><td>AV_NAME</td>
			<td>AV_KIND</td>
			<td>AV_RESULT</td>
			<td><a href="AV_TXT_LINK">txt report</td>
			<td><a href="AV_SCREEN_LINK"><img src="AV_SCREEN_LINK" width=150 height=150></a></td></tr>
		'''
	
		html_results = ""

		for s in res:
			html_table = html_section
			html_table = html_table.replace("AV_NAME",s['av'])
			html_table = html_table.replace("AV_KIND",s['kind'])
			html_table = html_table.replace("AV_RESULT",s['result'])
			html_table = html_table.replace("AV_TXT_LINK","results_%s_%s.txt" % (s['av'],s['kind']) )
			html_table = html_table.replace("AV_SCREEN_LINK","screenshot_%s_%s.png" % (s['av'],s['kind']) )
			html_results += html_table
		return html_results

	def _add_errors(self, errors):

		html_table_head = '''
		<table border=1 cellpadding=1 cellspacing=2 width=70%>
			<tr><td with=15%>Virtual Machine</td>
				<td with=15%>Kind of test</td>
				<td width=50%>Result</td>
				<td width=10%>TXT Report</td>
				<td width=10%>Screenshot</td></tr>
		'''	

		html_section = '''
		<tr><td>AV_NAME</td>
			<td>AV_KIND</td>
			<td>AV_ERROR</td>
			<td><a href="AV_TXT_LINK">txt report</a></td>
			<td><a href="AV_SCREEN_LINK"><img src="AV_SCREEN_LINK" width=150 height=150></a></td></tr>
		'''

		html_errs = html_table_head
		
		for e in errors:
			html_table = html_section
			html_table = html_table.replace( "AV_NAME", e['av'] )
			html_table = html_table.replace("AV_KIND", e['kind'])
			html_table = html_table.replace( "AV_ERROR", e['result'] )
			html_table = html_table.replace( "AV_TXT_LINK", "results_%s_%s.txt" % (e['av'],e['kind']) )
			html_table = html_table.replace( "AV_SCREEN_LINK", "screenshot_%s_%s.png" % (e['av'],e['kind']) )
			html_errs += html_table
		html_errs += "</table>"

		return html_errs



	def _write_html_report(self, result, html_file_name=None):

		html_table_closed = '</table>'

		content  = ""
		content += "<html><body>"
		content += "<h2>%s</h2>" % datetime.datetime.now()

		if len(result['failed']) > 0:
			content +=  self._add_header("Failed") 
			content +=  self._add_results(result['failed'] )
			content +=  html_table_closed 

		if len(result['errors']) > 0:
			content +=  "<h2>Errors</h2>"
			content +=  self._add_errors(result['errors'])

		if len(result['success']) > 0:
			content +=  self._add_header("Success") 
			content +=  self._add_results(result['success'])
			content +=  html_table_closed 

		content += "</body></html>"

		if html_file_name is None:
			return content
		else:
			f = open(html_file_name, 'wb') 
			f.write(content)
			f.close()

	def _get_results(self):
		errors  = []
		success = []
		failed  = []

		record  = {}
		
		for result in self.results:
			for r in result:
				record = {}
				l = r.split(",")

				if len(l) == 3:
					record['av']     = l[0].strip()
					record['kind']   = l[1].strip()
 					record['result'] = l[2].strip()
					errors.append(record)

				elif len(l) == 4:
					record['av']     = l[0].strip()
					record['kind']   = l[1].strip()
					record['result'] = l[3].replace("\r\n","").replace("+","").strip()

					if "SUCCESS" in record['result']:
						success.append(record)

					elif "FAILED" in record['result']:
						failed.append(record)

		res_list = {} 
		res_list["success"] = success
		res_list["errors"]  = errors
		res_list["failed"]  = failed

		return res_list

	def save_html(self, html_file, on_file=True):
		print "saving in %s" % html_file
		res_list = self._get_results()
		if on_file is True:
			self._write_html_report(res_list, html_file)
		else:
			self._write_html_report(res_list)
	
	def send_mail(self):
		if self.report is None:
			return False
		try:
			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor"
			msg["From"] = "avmonitor@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com"
			body = MIMEText(self.report)
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			#smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.sendmail(msg["From"], msg["To"], msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False


	def _build_mail_body(self,  url_dir):

		hresults = []
		hcolumns = ['name']

		host = "172.20.20.167"
		port = "8080"

		report_file = "http://%s:%s/%s/report_dispatch.html" % ( host, port, url_dir )

		sortedresults = sorted(self.results, key = lambda x: x[0][0])
		print "DBG sorted %s" % sortedresults

		for av in sortedresults:
			name = av[0].split(",")[0]
			k = len(av)

			hres = []
			hres.append(name)

			for ares in av:
				r = ares.split(", ")
				hres.append(r[-1])
				if r[1] not in hcolumns:
					hcolumns.append(r[1])

			hresults.append(hres)


		print "DBG hresults %s" % hresults
		style  = """
<html>
<style type'text/css'>
#success-div {
    background-color: green;
    width: 20px;
    height: 10px;
}
#error-div {
    background-color: black;
    width: 20px;
    height: 10px;
}
#failed-div {
    background-color: red;
    width: 20px;
    height: 10px;
}
#blacklisted-div {
	background-color: grey;
	width: 20px;
	height: 10px;
}
a.fill-div {
    display: block;
    height: 100%;
    width: 100%;
    text-decoration: none;
}
</style>
<body>		
		"""

		header_st = "<table><tr>"
		header_en = "</tr>"
		linestart = "<tr><td>%s</td>"
		linetoken = "<td id='%s-div'><a href='%s' class='fill-div'></a></td>"
		lineend   = "</tr>"
		legend    = "</table><p>Legend:</p><table><tr><td id=success-div></td><td>SUCCESS</td><tr><td id=failed-div></td><td>FAILED</td><tr><td id=error-div></td><td>ERROR</td><tr><td id=blacklisted-div></td><td>BLACKLISTED</td></tr></table>"
		footer    = "<br><br><b>View full <a href='%s'>report</a><b></body></html>" % report_file

		content = style 

		header = header_st

		for col in hcolumns:
			header += "<td>%s</td>" % col

		header += header_en
		content += header

		for res in hresults:
			rd = dict(zip(hcolumns,res))
			print "DBG rd %s" % rd
			#rd['name'], rd['silent'], rd['melt'], rd['exploit']
			avname = rd['name']
			l = linestart % avname
			for col in hcolumns[1:]:
				link = "http://%s:%s/%s/results_%s_%s.txt" % (host, port, url_dir, avname, col)

				for kind in ["FAILED", "BLACKLISTED", "SUCCESS", "ERROR"]:
					if kind in rd[col]:
						l+= linetoken % (kind.lower(), link)
						break
			l += lineend

			content += l

		content += legend
		content += footer

		return content

	def send_report_color_mail(self,  url_dir):
		content = self._build_mail_body(url_dir)

		try:
			msg = MIMEMultipart()
			msg["Subject"] = "AV Monitor Results"
			msg["From"] = "avmonitor@hackingteam.com"
			msg["To"] = "olli@hackingteam.com,zeno@hackingteam.com,alor@hackingteam.com"
			body = MIMEText(content, 'html')
			msg.attach(body)
			smtp = smtplib.SMTP("mail.hackingteam.com", 25)
			smtp.sendmail(msg["From"], msg["To"].split(","), msg.as_string())
			smtp.quit()
			return True
		except Exception as e:
			print "[report:send mail] Impossible to send report via mail. Exception: %s" % e
			return False



	def _sort_results(self):
		hcolumns = ['name']
		hresults = []
		sortedresults = sorted(self.results, key = lambda x: x[0][0])

		for av in sortedresults:
			name = av[0].split(",")[0]
			k = len(av)

			hres = []
			hres.append(name)

			for ares in av:
				r = ares.split(", ")
				hres.append(r[-1])
				if r[1] not in hcolumns:
					hcolumns.append(r[1])

			hresults.append(hres)

		return hresults
	
	def save_db(self, test_id):
		try:

			results = self._sort_results()

			for result in results:
				r = DBReport(test_id, result[0], result[1], result[2], result[3])
				db.session.add(r)
			
			db.session.commit()
			return True
		except Exception as e:
			print "DBG error. Exception: %s" % e
			return False
	
'''
if __name__ == "__main__":
	results = [ ["AV1, silent, SUCCESS","AV1, melt, SUCCESS","AV1, exploit, SUCCESS"], 
				["AV2, silent, FAILED","AV2, melt, FAILED","AV2, exploit, FAILED"],
				["AV3, silent, ERROR","AV3, melt, ERROR","AV3, exploit, ERROR"] ]

	r = Report(results)
	print r.sort_results()
'''