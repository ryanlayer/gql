#!/sw/bin/python
import ply.lex as lex
import ply.yacc as yacc
import gqltokens
import gqlgrammar
import gqlinterp
import gqltools
import sys
import tempfile
import parsetab



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
