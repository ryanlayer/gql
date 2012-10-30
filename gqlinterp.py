import os.path
import gqltools

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

def eval_elt(elt, env):
	#print elt # DEBUG
	env_update('curr line', elt[1], env)
	if elt[0] == 'stmt':
		eval_stmt(elt[2], env)
	else:
		raise Exception('unknown  element ' + elt, 'eval_elt')
		#print "ERROR: eval_elt: unknown element " + elt

def eval_stmts(stmts, env):
	for stmt in stmts:
		eval_stmt(stmt, env)

def eval_stmt(stmt, env):
	#print stmt # DEBUG
	stype = stmt[0]
	if stype == 'assign':
		vname = stmt[1]
		rhs = stmt[2]
		env_update(vname, eval_exp(rhs, env), env)

	elif stype == 'print':
		#('print', ('identifier', 'c'))
		ident = eval_exp(stmt[1],env)
		gqltools.print_file(ident)

	elif stype == 'save':
		#('save', ('identifier', 'c'), ('file', ('string', 'test.bed')))
		ident = eval_exp(stmt[1],env)
		file_path = eval_exp(stmt[2], env)
		gqltools.save_file(ident, file_path)


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
			raise Exception('unbound variable ' + vname, 'identifier')
		else:
			return value
	#}}}
	
	#{{{ if etype == 'load':
	if etype == 'load':
		# ('load', 
		#	('file', ('string', 'file0')), 
		#	('filetype', 'GENOME'))

		file_path = eval_exp(exp[1], env)

		# make sure file exists
		if ( not os.path.isfile(file_path) ):
			raise Exception ('file not found ' + file_path, 'load')

		filetype_name = eval_exp(exp[2], env)
		
		# make sure the type is correct
		if gqltools.verify_filetype(file_path, filetype_name) == True:
			return {'val':file_path, 'type':filetype_name, 'tmp':False}
		else:
			raise Exception('Incorrect filetype ' + filetype_name + " " +
					file_path)
	#}}}

	#{{{ elif etype == 'intersect':
	elif etype == 'intersect':
		# ('intersect',
		#	[('identifier', 'a'), ('identifier', 'b')])
		idents = exp[1]
		bedfiles = []
		types = []
		for ident in idents:
			bedx = eval_exp(ident, env)
			bedfiles = bedfiles + [ bedx ]
			types = types + [ bedx['type'] ]

		labels = []
		for ident in idents:
			labels = labels + [ident[1]]

		result_file = gqltools.intersect_beds(bedfiles)	

		return {'val':result_file['val'],
				'labels':labels,
				'type':'BEDN',
				'types':types,
				'tmp':True}
	#}}}

	#{{{ elif etype == 'intersect':
	elif etype == 'subtract':
		# ('subtract',
		#	[('identifier', 'a'), ('identifier', 'b')])
		idents = exp[1]
		bedfiles = []
		types = []
		for ident in idents:
			bedfiles = bedfiles + [ eval_exp(ident, env) ]

		result_file = gqltools.subtract_beds(bedfiles)	

		return {'val':result_file['val'],
				'type':result_file['type'],
				'tmp':True}
	#}}}

	elif etype == 'file':
		#   ('file', ('string', 'file0'))
		return eval_exp(exp[1], env)

	elif etype == 'filetype':
		#	('filetype', 'GENOME'))
		#return eval_exp(exp[1], env)
		return exp[1]

	elif etype == "string":
		#   ('string', 'file0')
		return exp[1]

	elif etype == 'number':
		return float(exp[1])

	else:
		print "ERROR: unknown expression type ",
		print etype
	return None

def interpret(ast):
	global_env = (None, {}) 
	for elt in ast:
		try:
  			eval_elt(elt,global_env) 
		except Exception as e:
			msgs = e.args
			print 'ERROR: '	+ str(msgs[0]) + " line:"  + \
				str(env_lookup('curr line',global_env))
	#env_debug(global_env) #Debug
	

def interpret_cmdline(ast,global_env):
	for elt in ast:
		try:
  			eval_elt(elt,global_env) 
		except Exception as e:
			msgs = e.args
			print 'ERROR: '	+ str(msgs[0]) + " line:"  + \
				str(env_lookup('curr line',global_env))
