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
import logging
import optparse

LOGGING_LEVELS = {	'critical': logging.CRITICAL,
					'error': logging.ERROR,
					'warning': logging.WARNING,
					'info': logging.INFO,
					'debug': logging.DEBUG}

parser = optparse.OptionParser()
parser.add_option('-l', '--logging-level', help='Logging level')
parser.add_option('-f', '--logging-file', help='Logging file name')
(options, args) = parser.parse_args()
logging_level = LOGGING_LEVELS.get(options.logging_level,
							logging.NOTSET)
logging.basicConfig(level=logging_level,
					filename=options.logging_file,
					format='%(asctime)s %(levelname)s: %(message)s',
					datefmt='%Y-%m-%d %H:%M:%S')

gqllexer    = lex.lex(module=gqltokens)
gqlparser   = yacc.yacc(module=gqlgrammar)
global_env = (None, {})

#if sys.stdin:
	#for line in sys.stdin:
		#gqlast = gqlparser.parse(line,lexer=gqllexer,tracking=True)
		#result = gqlinterp.interpret_cmdline(gqlast, global_env)
	#gqltools.clear_tmp_files()
#elif len(sys.argv) == 1:
if len(sys.argv) == 1:
	while 1:
		try:
			data = raw_input('> ')
		except EOFError:
			break
		if not data: continue
		gqlast = gqlparser.parse(data,lexer=gqllexer,tracking=True)
		result = gqlinterp.interpret_cmdline(gqlast, global_env)
	gqltools.clear_tmp_files()
else:
	f = open(sys.argv[1], 'r')
	data = f.read()
	f.close()
	gqlast = gqlparser.parse(data,lexer=gqllexer,tracking=True)
	result = gqlinterp.interpret(gqlast)
	gqltools.clear_tmp_files()
