import os.path
import gqltools
import sys

#{{{ def env_lookup|update|debug
def env_lookup(vname,env):
	if vname in env[1]:
		return (env[1])[vname]
	else:
		return None

def env_update(vname, value, env):
	(env[1])[vname] = value

def env_debug(env):
	print "Evironment Debug:"
	for vname in env[1]:
		print "  evn[" + vname + "] = ",
		print (env[1])[vname]
#}}}

#{{{def eval_elt(elt, env):
def eval_elt(elt, env):
	#print elt # DEBUG
	env_update('curr line', elt[1], env)
	if elt[0] == 'stmt':
		eval_stmt(elt[2], env)
	else:
		raise Exception('unknown  element ' + elt, 'eval_elt')
		#print "ERROR: eval_elt: unknown element " + elt
#}}}

#{{{ def eval_stmts(stmts, env):
def eval_stmts(stmts, env):
	for stmt in stmts:
		eval_stmt(stmt, env)
#}}}

#{{{ def eval_stmt(stmt, env):
def eval_stmt(stmt, env):
	#print stmt # DEBUG
	stype = stmt[0]

	#{{{if stype == 'assign':
	if stype == 'assign':
		vname = stmt[1]
		rhs = stmt[2]
		env_update(vname, eval_exp(rhs, env), env)
	#}}}

	#{{{elif stype == 'print':
	elif stype == 'print':
		#('print', ('identifier', 'c'))
		ident = eval_exp(stmt[1],env)
		gqltools.print_bedx(ident)
	#}}}

	#{{{elif stype == 'save':
	elif stype == 'save':
		#('save', ('identifier', 'c'), ('file', ('string', 'test.bed')))
		ident = eval_exp(stmt[1],env)
		file_path = eval_exp(stmt[2], env)
		gqltools.save_file(ident, file_path)
	#}}}

	#{{{elif stype == 'count':
	elif stype == 'count':
		#print stmt
		#('count', ('identifier', 'e'))
		ident = eval_exp(stmt[1],env)
		gqltools.count(ident)
	#}}}
#}}}

#{{{def eval_exp(exp, env):
def eval_exp(exp, env):
	#print exp # DEBUG
	etype = exp[0]

	#{{{ if etype == "identifier":
	if etype == "identifier":
		#print exp #Debug
		# ('identifier', 'b')
		vname = exp[1]
		value = env_lookup(vname,env)
		if value == None:
			#print "ERROR: unbound variable " + vname
			raise Exception('Unbound variable ' + vname, 'identifier')
		else:
			return value
	#}}}
	
	#{{{ if etype == 'load':
	if etype == 'load':
		# ('load', 
		#	('file', ('string', 'file0')), 
		#	('filetype', 'GENOME'))

		file_path = eval_exp(exp[1], env)


		#filetype_name = eval_exp(exp[2], env)
		filetype_name = 'auto'
		
		# make sure the type is correct
		return gqltools.load_file(file_path, filetype_name)
	#}}}

	#{{{ if etype == 'cast':
	if etype == 'cast':
		#('cast', ('identifier', 'a'), ('filetype', 'BED6'), [])
		ident = exp[1]
		bedx = eval_exp(ident, env)
		new_type = eval_exp(exp[2],env)

		return gqltools.cast(bedx,  new_type)
	#}}}

	#{{{ elif etype == 'binary-intersect':
	elif etype == 'binary-intersect':
		#print exp
		#('binary-intersect', 
		#	[('identifier', 'a')], 
		#	[('identifier', 'b'), ('identifier', 'c'), ('identifier', 'd')])
		idents = exp[1]
		n_bedfiles = []
		for ident in idents:
			bedx = eval_exp(ident, env)
			n_bedfiles = n_bedfiles + [ bedx ]

		n_labels = []
		for ident in idents:
			n_labels = n_labels + [ident[1]]

		idents = exp[2]
		m_bedfiles = []
		for ident in idents:
			bedx = eval_exp(ident, env)
			m_bedfiles = m_bedfiles + [ bedx ]

		m_labels = []
		for ident in idents:
			m_labels = m_labels + [ident[1]]

		return gqltools.binary_intersect_beds(n_bedfiles, \
											  n_labels, \
											  m_bedfiles, \
											  m_labels)

	#}}}

	#{{{ elif etype == 'unary-intersect':
	elif etype == 'unary-intersect':
		# ('intersect',
		#	[('identifier', 'a'), ('identifier', 'b')])
		idents = exp[1]
		bedfiles = []
		for ident in idents:
			bedx = eval_exp(ident, env)
			bedfiles = bedfiles + [ bedx ]

		labels = []
		for ident in idents:
			labels = labels + [ident[1]]

		return gqltools.unary_intersect_beds(bedfiles, labels)	
	#}}}

	#{{{ elif etype == 'subtract':
	elif etype == 'subtract':
		# ('subtract',
		#	[('identifier', 'a'), ('identifier', 'b')])
		idents = exp[1]
		bedfiles = []
		types = []
		for ident in idents:
			bedfiles = bedfiles + [ eval_exp(ident, env) ]

		return gqltools.subtract_beds(bedfiles)	
	#}}}

	#{{{ elif etype == 'mergemin':
	elif etype == 'mergemin':
		print exp
		ident_list = exp[1]
		if len(ident_list) == 1:
			bednfile = eval_exp(ident, env)
			result_file = gqltools.mergemin_bedn(bednfile)	

		return result_file

	#}}}

	#{{{ elif etype == 'merge':
	elif etype == 'merge':
		#print exp # Debug
		# ('merge', 
		#	[('identifier', 'a'), ('identifier', 'b'), ('identifier', 'c')], 
		#	('score', ('function', 'MIN'), None))
		# or
		# ('merge', 
		#	[('identifier', 'a'), ('identifier', 'b'), ('identifier', 'c')], 
		#	None)
		idents = exp[1]
		modifiers = exp[2]
		bedfiles = []
		for ident in idents:
			bedx = eval_exp(ident, env)
			bedfiles = bedfiles + [ bedx ]

		mods = {}
		for modifier in modifiers:
			modifier_type = modifier[0]

			if modifier_type in mods:
				raise Exception('Multiple definitions of ' + \
						modifier_type + '.')

			if modifier_type == 'score':
				#('score', ('function', 'MIN'))
				function_type = eval_exp(modifier[1], env)
				mods['score'] = function_type

			elif modifier_type == 'distance':
				#('distance', ('number', 10.0))
				number = eval_exp(modifier[1], env)
				mods['distance'] = number

		return gqltools.merge_beds(bedfiles, mods)
	#}}}

	#{{{ simple rules
	elif etype == 'file':
		#   ('file', ('string', 'file0'))
		return eval_exp(exp[1], env)

	elif etype == 'filetype':
		#	('filetype', 'GENOME'))
		return exp[1]

	elif etype == "string":
		#   ('string', 'file0')
		return exp[1]

	elif etype == 'number':
		return float(exp[1])

	elif etype == 'function':
		return exp[1]

	else:
		print "ERROR: unknown expression type ",
		print etype
	return None
	#}}}
#}}}

#{{{def interpret(ast):
def interpret(ast):
	global_env = (None, {}) 
	for elt in ast:
		try:
  			eval_elt(elt,global_env) 
		except Exception as e:
			msgs = e.args
			print 'ERROR: '	+ str(msgs[0]) + " line:"  + \
				str(env_lookup('curr line',global_env))
			sys.exit(1)	
	return 0
	#env_debug(global_env) #Debug
#}}}	

#{{{ def interpret_cmdline(ast,global_env):
def interpret_cmdline(ast,global_env):
	for elt in ast:
		try:
  			eval_elt(elt,global_env) 
		except Exception as e:
			msgs = e.args
			print 'ERROR: '	+ str(msgs[0]) + " line:"  + \
				str(env_lookup('curr line',global_env))
			sys.exit(1)	
	return 0
#}}}
