import ply.lex as lex

reserved = (
	'INTERSECT',
	'SUBTRACT',
	'MERGEMIN',
	'MERGE',
	'LOAD',
	'CAST',
	'DISTANCE',
	'PRINT',
	'SAVE',
	'COUNT',
	'AS',
	'WHERE',
	'SCORE',
	'MIN',
	'SUM',
	'MAX',
	'MEAN',
	'MODE',
	'STDEV',
	'GENOME',
	'BED3',
	'BED6',
	'BED12',
)

tokens = (
		'NUMBER',		# 10
		#'PLUS',			# +
		#'MINUS',		# -
		#'TIMES',		# *
		#'DIVIDE',		# /
		#'EQUALEQUAL',	# ==
		'EQUAL',		# =
		'COMMA',		# ,
		'LPAREN',		# (
		'RPAREN',		# )
		'SEMICOLON',	# ;
		#'COLON',		# :
		'STRING',		# "has\"escaped\"quotes"
		'IDENTIFIER',	# INTERSECT LOAD ...
) + reserved

t_ignore = ' \t\v\r'

t_ignore_COMMENT = '\#.*'

def t_newline(t):
	r'\n'
	t.lexer.lineno += len(t.value)


t_COMMA = r','
#t_DIVIDE = r'/'
#t_EQUALEQUAL = r'=='
t_EQUAL = r'='
t_SEMICOLON = r';'
#t_COLON = r':'
#t_PLUS = r'\+'
#t_MINUS = r'-'
#t_TIMES = r'\*'
t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_NUMBER(t):
	r'-?[0-9]+(\.[0-9]*)?'
	t.value = float(t.value)
	return t

def t_STRING(t):
	r'"([^"\\]|(\\.))*"'
	t.value = t.value[1:-1]
	return t

def t_IDENTIFIER(t):
	r'[a-zA-Z]+[a-zA-Z0-9_]*'
	if t.value in reserved:
			t.type = t.value
	return t

def t_error(t):
	print "Illegal character '%s'" % t.value[0]
	t.lexer.skip(1)

def find_column(input, token):
	last_cr = input.rfind('\n', 0, token.lexpos)
	if last_cr < 0:
		last_cr = 0
	column = (token.lexpos - last_cr) + 1
	return column
