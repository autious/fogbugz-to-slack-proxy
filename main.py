#!/usr/bin/python

import SimpleHTTPServer
import SocketServer
import urllib
import json
import requests
import sys

values_of_interest = [
	"assignedtoname",
	"customeremail",
	"title",
	"eventtype"
]

value_translation = {
	"assignedtoname" : "Assigned",
	"customeremail" : "Email",
	"title" : "Title",
	"eventtype" : "Event Type"
}

size_translation = {
	"assignedtoname" : True,
	"customeremail" : True,
	"title" : True,
	"eventtype" : True
}



if len(sys.argv) == 3:

	response_url = sys.argv[1]
	PORT = sys.argv[2]

	print "Responding to " + response_url + " listening to " + PORT

	from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
	from cgi import parse_header, parse_multipart, parse_qs

	class Handler(BaseHTTPRequestHandler):
		def do_POST(self):
			ctype, pdict = parse_header(self.headers.getheader('content-type'))
			length = int(self.headers.getheader('content-length'))
			data = urllib.unquote(self.rfile.read(length))

			print "Got Message"
			json_msg = json.loads(data)

			print json.dumps(json_msg, indent=4)

			print "From: " + str(self.client_address[0])

			caseeventid = json_msg["caseeventid"]
			casenumber = json_msg["casenumber"]

			fields = []

			for k,v in json_msg.iteritems():
				if k in values_of_interest:
					fields.append( {
						"title": value_translation[k],
						"value": v,
						"short": size_translation[k]
					})

			payload = {
				"text": "Update on Issue <https://humble.fogbugz.com/default.asp?" + str(casenumber) + "#" + str(caseeventid) + "|" + str(json_msg["casenumber"]) + ">",
				"attachments": [ {
					"pretext": "",
					"fallback": "",
					"text": "",
					"color": "",
					"mrkdwn_in": ["text", "title", "fallback"],
					"fields": fields
				} ]
			}

			headers = {'content-type': 'application/json'}

			response = requests.post(response_url, data=json.dumps(payload), headers=headers)

			print response

			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

	httpd = SocketServer.TCPServer(("", int(PORT)), Handler)

	print "serving at port", PORT

	httpd.serve_forever()
else:
	print "Usage main.py <slack-webhook-token> <listening-port>"
	print "you gave " + str(len(sys.argv))
