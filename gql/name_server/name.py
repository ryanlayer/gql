#!/usr/local/bin/python --
import cgi
import urllib2
import cgitb
import json

import xml.etree.ElementTree as ET

json_data=open('name.conf')
config = json.load(json_data)

print "Content-Type: text/html"
print

f = cgi.FieldStorage()

if 'path' in f:
	file = urllib2.urlopen(config['names_path'])
	data = file.read()
	file.close()

	path = f['path'].value.split(':')

	curr_root = ET.fromstring(data)

	for step in path:
		found = False
		for child in curr_root:
			if step == child.attrib['name']:
				curr_root = child
				found = True
				break
		if not found:
			break

	if found:
		url_list = []
		if curr_root.tag == 'track':
			label = f['path'].value 
			url_list.append([label,curr_root.attrib['url']])
		elif curr_root.tag == 'group':
			for child in curr_root:
				if child.tag == 'track':
					label = f['path'].value + ':' + child.attrib['name']
					url_list.append([label,child.attrib['url']])

		print json.dumps(url_list)
