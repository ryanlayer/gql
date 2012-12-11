import os.path
import gqltools
import gqltypes
import sys

#{{{class InterpException(Exception):
class InterpException(Exception):
	def __init__(self, msg, method):
		self.msg = msg 
		self.method = method 
	def __str__(self):
		return msg + ':' + method
#}}}

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
		if elt[2]:
			eval_stmt(elt[2], env)
	else:
		raise InterpException('unknown  element ' + elt, 'eval_elt')
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
		gqltools.print_val(ident,-1)
	#}}}

	#{{{elif stype == 'peak':
	elif stype == 'peak':
		ident = eval_exp(stmt[1],env)
		num = stmt[2]
		gqltools.print_val(ident,num)
	#}}}

	#{{{elif stype == 'save':
	elif stype == 'save':
		#('save', ('identifier', 'c'), ('file', ('string', 'test.bed')))
		ident = eval_exp(stmt[1],env)
		file_path = eval_exp(stmt[2], env)
		gqltools.save_file(ident, file_path)
	#}}}

	#{{{elif stype == 'plot':
	elif stype == 'plot':
		ident = eval_exp(stmt[1],env)
		file_path = eval_exp(stmt[2], env)
		gqltools.plot_val(ident, file_path)
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
			raise InterpException('Unbound variable ' + vname, 'identifier')
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

	#{{{ if etype == 'sort':
	if etype == 'sort':
		ident = exp[1]
		bedx = eval_exp(ident, env)
		return gqltools.sort_bedx(bedx)
	#}}}

	#{{{ if etype == 'cast':
	if etype == 'cast':
		print exp
		#('cast', ('identifier', 'a'), ('filetype', 'BED6'), [])
		ident = exp[1]
		bedx = eval_exp(ident, env)
		new_type = eval_exp(exp[2],env)
		print bedx
		print new_type

		return gqltools.cast(bedx,  new_type)
	#}}}

	#{{{ if etype == 'hilbert':
	if etype == 'hilbert':
		#print exp
		# ('hilbert',
		#  ('identifier', 'a'), 
		#  [('chrom',
		#     ('function', 'BOOLEAN', [('compare', ('==', ('string', 'chr1')))])), 
		#   ('genome',
		#	  ('function', 'BOOLEAN', [('compare', ('==', ('string', 'hg19')))])),
		#   ('dimension', 8.0)])
		#
		# ('hilbert', 
		#  ('identifier', 'a'),
		#  [('chrom',
		#    ('function', 'BOOLEAN', [('compare', ('==', ('string', 'chr1')))])),
		#   ('genome',
		#    ('function', 'BOOLEAN', [('compare', ('==', ('identifier', 'g')))])), 
		#   ('dimension', 128.0)])
		#
		# ('hilbert', 
		#  ('identifier', 'a'),
		#  [('chrom', 
		#    ('function', 'EXPRESSION', ('string', 'chr1'))), 
		#   ('genome',
		#    ('function', 'EXPRESSION', ('string', 'hg19'))),
		#   ('dimension', 128.0)])

		idents = exp[1]
		n_bedfiles = []
		for ident in idents:
			bedx = eval_exp(ident, env)
			n_bedfiles = n_bedfiles + [ bedx ]

		n_labels = []
		for ident in idents:
			n_labels = n_labels + [ident[1]]

		modifiers = exp[2] 
		mods = {}
		for modifier in modifiers:
			modifier_type = modifier[0]

			if modifier_type in mods:
				raise InterpException('Multiple definitions of ' + \
						modifier_type + ' in HILBERT.', 'hilbert')

			function = eval_exp(modifier[1], env)
			if function[0] not in ['EXPRESSION']:
				raise InterpException('Unsupported function type ' +
					function[0] + ' in HILBERT.', 'hilbert')

			mods[modifier_type] = eval_exp(function[1], env)

		r = gqltools.hilbert_curve_matrix(n_bedfiles, n_labels, mods)
	
		return r
	#}}}

	#{{{ if etype == 'complement':
	if etype == 'complement':
		#print exp
		#('complement', ('identifier', 'a'), ('identifier', 'g'))
		#('complement', ('identifier', 'a'), 'hg19')
		target_bed = eval_exp(exp[1],env)
		genome = exp[2]
		if not type(genome) is str:
			genome = eval_exp(genome,env)

		return gqltools.complement_bedx(target_bed, genome)

		#return gqltools.cast(bedx,  new_type)
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

	#{{{ elif etype == 'binary-jaccard':
	elif etype == 'binary-jaccard':
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

		return gqltools.binary_jaccard_beds(n_bedfiles, \
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
		ident = exp[1]
		bedfile = eval_exp(ident, env)
		idents = exp[2]
		bedfiles = []
		for ident in idents:
			bedfiles = bedfiles + [ eval_exp(ident, env) ]

		return gqltools.subtract_beds(bedfile, bedfiles)	
	#}}}

	#{{{ elif etype == 'mergemin':
	elif etype == 'mergemin':
		#print exp
		ident_list = exp[1]
		if len(ident_list) == 1:
			bednfile = eval_exp(ident, env)
			result_file = gqltools.mergemin_bedn(bednfile)	

		return result_file

	#}}}

	#{{{ elif etype == 'merge':
	elif etype == 'merge':
		print exp # Debug
		# ('merge', 
		#  'min',
		#  [('identifier', 'a'),
		#   ('identifier', 'b'),
		#   ('identifier', 'c') ],
		#  [('name', ('function', 'AGGREGATE', 'COLLAPSE')), 
		#   ('score', ('function', 'AGGREGATE', 'COUNT'))])
		merge_type = exp[1] #min,max,flat
		idents = exp[2]
		modifiers = exp[3] #should all be functions and AGGREGATE
		bedfiles = []
		for ident in idents:
			bedx = eval_exp(ident, env)
			bedfiles = bedfiles + [ bedx ]

		mods = {}
		for modifier in modifiers:
			modifier_type = modifier[0]

			if modifier_type in mods:
				raise InterpException('Multiple definitions of ' + \
						modifier_type + ' in MERGER.', 'merge')

			function = eval_exp(modifier[1], env)
			if function[0] != 'AGGREGATE':
				raise InterpException('Unsupported function type ' + \
						function[0] + ' in MERGE.', 'merge' )

			#mods[modifier_type] = eval_exp(modifier[1], env)
			mods[modifier_type] = function[1]

		return gqltools.merge_beds(merge_type,bedfiles, mods)
	#}}}

	#{{{ elif etype == 'filter':
	elif etype == 'filter':
		#print exp # Debug
		#('filter',
		#	[	('identifier', 'a'),
		#		('identifier', 'b'),
		#		('identifier', 'c'),
		#		('identifier', 'd')],
		#	[   ('score', ('function', 'BOOLEAN',
		#			[   ('compare', ('<', ('number', 100.0))),
		#				('conj', '&'),
		#				('compare', ('>', ('number', 50.0))),
		#				('conj', '&'),
		#				('compare', ('!=', ('number', 75.0)))
		#			])
		#		),
		#		('start', ('function', 'BOOLEAN',
		#			[   ('compare', ('>', ('number', 1000.0)))
		#			])
		#		),
		#		('end', ('function', 'BOOLEAN',
		#			[   ('compare', ('<', ('number', 10000.0)))
		#			])
		#		),
		#		('chrom', ('function', 'BOOLEAN',
		#			[ ('compare', ('==', ('string', 'chr1')))
		#			])
		#		)
		#	]
		#)

		idents = exp[1]
		modifiers = exp[2]
		bedxs = []
		for ident in idents:
			bedx = eval_exp(ident, env)
			bedxs = bedxs + [ bedx ]

		mods = {}
		for modifier in modifiers:
			modifier_type = modifier[0]

			if modifier_type in mods:
				raise InterpException('Multiple definitions of ' + \
						modifier_type + ' in FILTER.', 'filter')

			function = eval_exp(modifier[1], env)
			if function[0] != 'BOOLEAN':
				raise InterpException('Unsupported function type ' + \
						function[0] + ' in FILTER.','filter' )
			bool_funcs = []
			for element in function[1]:
				bool_func = []
				if element[0] == 'compare':
					op = element[1][0]
					val = element[1][1]
					if val[0] == 'number':
						bool_func = [op, val[1]]
					elif val[0] == 'string':
						bool_func = [op, '"' + val[1] + '"']
					else:
						raise InterpException(\
								'Unsupported value type ' + val[0] + \
								'in boolean ' + \
								'function in FILTER.','filter')
				elif element[0] == 'conj':
					conj = element[1][0]
					bool_func = [conj]
				else:
					raise InterpException(\
							'Error in boolean function in FILTER.','filter')
				bool_funcs.append(bool_func)
		
			mods[modifier_type] = bool_funcs

		return gqltools.filter_bedx(bedxs, mods)
	#}}}

	#{{{elif etype == 'count':
	elif etype == 'count':
			
		ident= eval_exp(exp[1], env)

		return gqltools.count(ident)

	#}}}

	#{{{ simple rules
	elif etype == 'file':
		#   ('file', ('string', 'file0'))
		return eval_exp(exp[1], env)

	elif etype == 'filetype':
		#	('filetype', 'GENOME'))
		return gqltypes.source_type_map[exp[1]]

	elif etype == "string":
		#   ('string', 'file0')
		return exp[1]

	elif etype == 'number':
		return float(exp[1])

	elif etype == 'function':
		if len(exp) == 2:
			return exp[1]
		else:
			return exp[1:]

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
			if elt:
				eval_elt(elt,global_env) 

		except InterpException as e:
			raise Exception(e.msg + \
				" line:" + str(env_lookup('curr line',global_env)))

		except gqltools.ToolsException as e:
			raise Exception(e.msg + \
				" line:" + str(env_lookup('curr line',global_env)))

		except Exception as e:
			msgs = e.args
			raise Exception(str(e) + \
				" line:" + str(env_lookup('curr line',global_env)))
	return 0
	#env_debug(global_env) #Debug
#}}}	

#{{{ def interpret_cmdline(ast,global_env):
def interpret_cmdline(ast,global_env):
	for elt in ast:
		try:
			if elt:
				eval_elt(elt,global_env) 
		except InterpException as e:
			raise Exception(e.msg)
		except gqltools.ToolsException as e:
			raise Exception(e.msg)
		except Exception as e:
			print type(e)
			msgs = e.args
			raise Exception(str(msgs[0]))
	return 0
#}}}
