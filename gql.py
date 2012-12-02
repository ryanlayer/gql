#!/usr/local/bin/python
import ply.lex as lex
import ply.yacc as yacc
import gqltokens
import gqlgrammar
import gqlinterp
import gqltools
import sys
import tempfile
import parsetab
import optparse
import json

json_data=open('gql.conf')
gqltools.config = json.load(json_data)

gqllexer    = lex.lex(module=gqltokens)
gqlparser   = yacc.yacc(module=gqlgrammar)
global_env = (None, {})

if len(sys.argv) == 1:
	while 1:
		try:
			data = raw_input('> ')
		except EOFError:
			break
		if not data: continue
		try:
			gqlast = gqlparser.parse(data,lexer=gqllexer,tracking=True)
			if gqlast:
				#try:
				result = gqlinterp.interpret_cmdline(gqlast, global_env)
				#except Exception as interp_e:
					#print interp_e
		except Exception as parse_e:
			print parse_e 
	gqltools.clear_tmp_files()
else:
	f = open(sys.argv[1], 'r')
	data = f.read()
	f.close()
	gqlast = gqlparser.parse(data,lexer=gqllexer,tracking=True)
	result = gqlinterp.interpret(gqlast)
	gqltools.clear_tmp_files()
