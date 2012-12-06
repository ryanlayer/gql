#!/usr/bin/env python
import ply.lex as lex
import ply.yacc as yacc
import os
from os.path import expanduser
import gqltokens
import gqlgrammar
import gqlinterp
import gqltools
import sys
import tempfile
import parsetab
import optparse
import json
import readline
import traceback
sys.path.append('./')

class SimpleCompleter(object):

	def __init__(self, options):
		self.options = sorted(options)
		return

	def complete(self, text, state):
		response = None
		#print str(text) + "," +str(state)
		if state == 0:
			# This is the first time for this text, so build a match list.
			if text:
				self.matches = [s 
								for s in self.options
								if s and s.startswith(text)]
			else:
				self.matches = self.options[:]

		# Return the state'th item from the match list,
		# if we have that many.
		try:
			response = self.matches[state]
		except IndexError:
			response = None
		return response

def determine_path ():
	"""Borrowed from wxglade.py"""
	try:
		root = __file__
		if os.path.islink (root):
			root = os.path.realpath (root)
		return os.path.dirname (os.path.abspath (root))
	except:
		print "I'm sorry, but something is wrong."
		print "There is no __file__ variable. Please contact the author."
		sys.exit ()

def main():
	curr_path = determine_path()
	json_data=open(curr_path + '/config/gql.conf')
	gqltools.config = json.load(json_data)

	gqllexer    = lex.lex(module=gqltokens)
	#gqlparser   = yacc.yacc(module=gqlgrammar,write_tables=0,debug=0)
	global_env = (None, {})

	history_file = expanduser("~/.gql_history")
	readline.set_completer(SimpleCompleter(gqltokens.reserved).complete)

	readline.parse_and_bind("tab: complete")

	if len(sys.argv) == 1:
		try:
			readline.read_history_file(history_file)
		except IOError:
			pass

		while True:
			try:
				data = raw_input('> ')
				if data != '':
					readline.write_history_file(history_file)
					#gqlast = None;
					try:
						gqlast = gqlparser.parse(data,\
												 lexer=gqllexer,\
												 tracking=True)
						if (gqlast != None):
							result = gqlinterp.interpret_cmdline(gqlast,\
																 global_env)
					except Exception as e:
						print str(e)
			except KeyboardInterrupt:
				print ''
				break
			except EOFError:
				print
				break
		gqltools.clear_tmp_files()
	else:
		f = open(sys.argv[1], 'r')
		data = f.read()
		f.close()
		gqlast = gqlparser.parse(data,lexer=gqllexer,tracking=True)
		result = gqlinterp.interpret(gqlast)
		gqltools.clear_tmp_files()

if __name__ == "__main__":
	main()
