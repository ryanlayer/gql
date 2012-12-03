#!/usr/local/bin/python
import ply.lex as lex
import ply.yacc as yacc
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

json_data=open('gql.conf')
gqltools.config = json.load(json_data)

gqllexer    = lex.lex(module=gqltokens)
gqlparser   = yacc.yacc(module=gqlgrammar)
global_env = (None, {})

history_file = expanduser("~/.gal_history")

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
				gqlast = None;
				try:
					gqlast = gqlparser.parse(data,lexer=gqllexer,tracking=True)
				except Exception as e:
					print "Parse error in input."
				if (gqlast != None):
					try:
						result = gqlinterp.interpret_cmdline(gqlast, global_env)
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
