import re
import gqlfiletypes
import gqltypes
import pybedtools
import random
import sys
import glob
import os.path
import os
import linecache
from collections import deque
import shutil
import numpy
import random
import urllib
import json
import scurgen

tmp_files = []
config = {}

class ToolsException(Exception):
	def __init__(self, msg, method):
		self.msg = msg 
		self.method = method 
	def __str__(self):
		return msg + ':' + method

#{{{ def load_config():
def load_config():
	json_data=open('gql.conf')
	config = json.load(json_data)
#}}}

#{{{ def add_tmp_file(tmp):
def add_tmp_file(tmp):
	tmp_files.append(tmp)
#}}}

#{{{ def clear_tmp_files():
def clear_tmp_files():
	while len(tmp_files) > 0:
		tmp_file = tmp_files.pop()
		if tmp_file.tmp:
			os.remove(tmp_file.val)
#}}}
		
#{{{ def get_temp_file_name(root_dir, prefix, postfix):
def get_temp_file_name(root_dir, prefix, postfix):

	tmp_file_name = root_dir + '/' + prefix + '.' + \
			str(random.randint(1,sys.maxint)) + '.' + \
			postfix

	while ( os.path.isfile(tmp_file_name) ):
		tmp_file_name = root_dir + '/' + prefix + '.' + \
				str(random.randint(1,sys.maxint)) + '.' + \
				postfix

	return tmp_file_name
#}}}

#{{{ def get_intersect_result(bed_pair):
def get_intersect_result(bed_pair):
	A = bed_pair[0]
	B = bed_pair[1]
	AB = bed_pair[2]

	R_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
									 'unary_intersect_beds', \
									 'tmp')

	offset = A.cols

#	if A.name == 'BED3':
#		offset = 3
#	elif A.name == 'BED6':
#		offset = 6
#	if A.name == 'BED12':
#		offset = 12 

	curr_line = 1

	out_file = open(R_file_name, 'w')
	in_file = open(AB.val, 'r')
	for line in in_file:
		cols = line.rstrip().split('\t')

		bed6_1 = cols[0:6]
		bed6_2 = cols[(offset + 0):(offset + 6)]

		bed6_r = [ bed6_1[0],
				   str( max(int(bed6_1[1]), int(bed6_2[1])) ),
				   str( min(int(bed6_1[2]), int(bed6_2[2])) ),
				   str(0),
				   str(curr_line),
				   bed6_1[5],
		]

		out_file.write("\t".join(bed6_r) + "\n")

		curr_line+=1
	in_file.close()
	out_file.close()

	R = gqltypes.BED6(R_file_name, True)

	add_tmp_file(R)

	return R
#}}}

#{{{def merge_bed_stack(out_stack):
def merge_bed_stack(out_stack):

	out_rows = deque()
	next_rows = []
	next_row_i = 0
	offset = 6

	while ( len(out_stack) > 0 ):
		A,B,AB = out_stack.pop()
		curr_next_rows = []
		curr_out_rows = []
		curr_row = 1

		in_file = open(AB.val, 'r')

		for line in in_file:
			curr_row_takes = 0

			if len(next_rows) == 0:
				curr_row_takes = 1
			else: 
				while ( (next_row_i < len(next_rows)) and
						( next_rows[next_row_i] == curr_row ) ):
					curr_row_takes += 1
					next_row_i += 1
				
			for i in range(0, curr_row_takes):
				cols = line.rstrip().split('\t')
				# the score in the first entry give the line number is the
				# associated file that pairs with the current line
				curr_next_rows.append(int(cols[4]) )
				if len(out_stack) > 0:
					# the 2nd and on entries have a pointer and a data entry,
					# pointer entries are BED6, so take all but the first 6
					# entries, also the last col is the size of the overlap,
					# ignore it
					curr_out_rows.append("\t".join(cols[6:-1]))
				else:
					# the first entry tin the stack does not have a pointer
					# entry, so take both 
					curr_out_rows.append("\t".join(cols[:-1]))

			curr_row+=1
		next_rows = curr_next_rows
		next_row_i = 0

		out_rows.appendleft(curr_out_rows)

	R_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
									 'unary_intersect_beds', \
									 'tmp')

	# check to make sure all the out_rows are the same length

	same_size = True
	for i in range(0, len(out_rows) - 1):
		same_size = same_size and \
				( len(out_rows[i]) == len(out_rows[i + 1]) )

	if not same_size:
		raise ToolsException('Unmached sizes in intersection', \
				'merge_bed_stack')


	out_file = open(R_file_name, 'w')

	for i in range(0, len(out_rows[0])):
		out_line = ''
		for j in range(0, len(out_rows)):
			if j != 0:
				out_line = out_line + '\t'
			out_line = out_line + (out_rows[j])[i]
		out_file.write(out_line + '\n')

	out_file.close()

	R = gqltypes.BEDN(R_file_name, True)

	add_tmp_file(R)

	return R
#}}}

#{{{ def binary_intersect_beds(ordered_bed_list_A, ordered_bed_list_B):
def binary_intersect_beds(_N_list, \
						  _N_labels, \
						  _M_list, \
						  _M_labels):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types


	(N_list, N_label) = make_mixed_list_with_labels(_N_list, \
													_N_labels, \
													allowed_types, \
													'INTERSECT')

	(M_list, M_label) = make_mixed_list_with_labels(_M_list, \
													_M_labels, \
													allowed_types, \
													'INTERSECT')

	NM_matrix = []
	for N in N_list:
		N_bed = pybedtools.BedTool( N.val )
		NM_list = []
		for M in M_list:
			M_bed = pybedtools.BedTool( M.val )
			try:
				NM_bed = N_bed.intersect(b=M_bed,wo=True)
			except pybedtools.helpers.BEDToolsError as e:
				raise ToolsException('Error in INTERSECT. ' + e.msg,\
						'binary_intersect_beds')
						

			NM = gqltypes.BEDN(NM_bed.fn,True)
			NM.types = [N.name,M.name]
			add_tmp_file(NM)
			NM_list.append(NM)
		NM_matrix.append(NM_list)

	return gqltypes.BEDM(NM_matrix,[N_label,M_label])
#}}}

#{{{ def binary_jaccard_beds(ordered_bed_list_A, ordered_bed_list_B):
def binary_jaccard_beds(_N_list, \
						  _N_labels, \
						  _M_list, \
						  _M_labels):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types

	(N_list, N_label) = make_mixed_list_with_labels(_N_list, \
													_N_labels, \
													allowed_types,\
													'JACCARD')

	(M_list, M_label) = make_mixed_list_with_labels(_M_list, \
													_M_labels, \
													allowed_types,\
													'JACCARD')

	num_matrix = []
	label_matrix = []
	for N in N_list:
		N_bed = pybedtools.BedTool( N.val )
		num_list = []
		for M in M_list:
			M_bed = pybedtools.BedTool( M.val )
			try:
				r = N_bed.jaccard(b=M_bed)
			except pybedtools.helpers.BEDToolsError as e:
				raise ToolsException('Error in JACCARD. ' + e.msg,\
						'binary_jaccard_beds')

			num = gqltypes.NUM(r['jaccard'])
			num_list.append(num)
		num_matrix.append(num_list)

	return gqltypes.NUMMATRIX(num_matrix,[N_label,M_label])
#}}}
	
#{{{ def unary_intersect_beds(ordered_bed_list, bed_labels):
def unary_intersect_beds(_N_list, _N_labels):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types

	(N_list, N_labels) = make_mixed_list_with_labels(_N_list,\
													 _N_labels,\
													 allowed_types,\
													 'INTERSECT')

	N_types = []
	for N in N_list:
		N_types.append(type(N))
	

	bed_queue = deque(N_list)
	out_stack = []
	while ( len(bed_queue) > 1 ):
		A = bed_queue.popleft()
		A_bed = pybedtools.BedTool( A.val )

		B = bed_queue.popleft()
		B_bed = pybedtools.BedTool( B.val )

		#intersect the top two bed files in the stack
		try:
			AB_bed = A_bed.intersect(b=B_bed,wo=True)
		except pybedtools.helpers.BEDToolsError as e:
			raise ToolsException('Error in INTERSECT. ' + e.msg,\
					'unary_intersect_beds')

		AB = gqltypes.BEDN(AB_bed.fn, True)

		add_tmp_file(AB)

		#extract the common intervals between the two bed files
		#and put the that set on the top of the stack
		R = get_intersect_result( [A, B, AB] )

		bed_queue.appendleft(R)
		out_stack.append( [A, B, AB] )

	#merge_bed_stack only sets val, type, and tmp fields
	#must add labeles and types
	R = merge_bed_stack(out_stack)
	R.labels = N_labels
	R.types = N_types

	return R
#}}}

#{{{ def subtract_beds(bedx, _N_list):
def subtract_beds(bedx, _N_list):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types

	N_list = make_mixed_list(_N_list, allowed_types,'SUBTRACT')

	if not (type(bedx) in gqltypes.flat_bed_types):
		raise ToolsException('Type mismatch in SUBTRACT. ' + \
				bedx.name + ' not supported.',\
				'subtract_beds')

	bed_queue = deque([bedx] + N_list)
	while ( len(bed_queue) > 1 ):
		pybedtools.settings.KEEP_TEMPFILES=True
		A = bed_queue.popleft()
		A_bed = pybedtools.BedTool( A.val )

		B = bed_queue.popleft()
		B_bed = pybedtools.BedTool( B.val )

		try:
			AB_bed = A_bed.subtract(b=B_bed,A=True)
		except pybedtools.helpers.BEDToolsError as e:
			raise ToolsException('Error in SUBTRACT. ' +  e.msg,\
					'subtract_beds')

		AB = A.__class__(AB_bed.fn, True)
		add_tmp_file(AB)

		bed_queue.appendleft(AB)

	return bed_queue.popleft()
#}}}

#{{{ def merge_beds(N_list, merge_opts):
def merge_beds(merge_type, _N_list, merge_opts):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types

	N_list = make_mixed_list(_N_list, allowed_types,'MERGE')

	input_types = []

	for bed in N_list:
		input_types.append(type(bed))

	# Parse input arguments and add/modify default argumetns
	# Default args
	valid_args = {'distance':'d', \
				  'score':'scores', \
				  'name':'nms', \
				  'stranded':'s'}

	score_functions = { 'MIN':'min', 'MAX':'max', 'SUM':'sum', \
			'MEAN':'mean', 'MEDIAN':'median', 'MODE':'mode', \
			'ANITMODE':'antimode', 'COLLAPSE':'collapse',
			'COUNT':'count'}

	kwargs = {}

	for merge_opt in merge_opts:
		if not ( merge_opt in valid_args ):
			raise ToolsException('Invalid option in MERGE. ' + \
						merge_opt + ' not supported.',\
						'merge_beds')

		if merge_opt == 'score':
			if not ( merge_opts[ merge_opt ] in score_functions ) :
				raise ToolsException(\
						'SCORE funciton not supported by MERGE. ' + \
						merge_opts[ merge_opt ],
						'merge_beds')
			else:
				kwargs[ valid_args[ merge_opt ] ] = \
						score_functions[ merge_opts[ merge_opt ] ]
		elif merge_opt == 'stranded':
			if (gqltypes.BED3 in input_types ) or \
				( gqltypes.BED4 in input_types) or \
				( gqltypes.BED5 in input_types)  :
				raise ToolsException(\
						'Type mismatch in MERGE. Cannot match by ' + \
						'strand with givne input types',\
						'merge_beds')
			kwargs[ valid_args[ merge_opt ] ] = True

		elif (merge_opt == 'distance'):
			if merge_type == 'flat':
				raise ToolsException('DISTANCE not supported for MERGEFLAT',\
						'merge_beds')
			elif merge_type == 'min':
				raise ToolsException('DISTANCE not supported for MERGEMIN',\
						'merge_beds')
			elif merge_type == 'max':
				raise ToolsException('DISTANCE not supported for MERGEMAX',\
						'merge_beds')
			else:
				kwargs[ valid_args[ merge_opt ] ] = merge_opts[ merge_opt ]

		elif (merge_opt == 'name'):
			if merge_opts[ merge_opt ] == 'COLLAPSE':
				kwargs[ valid_args[ merge_opt ] ] = True
			else :
				raise ToolsException(\
						'NAME funciton not supported by MERGE. ' + \
						merge_opts[ merge_opt ],
						'merge_beds')
	

	output_type = gqltypes.BED3
	if (len(kwargs) > 0) :
		output_type = gqltypes.BED6

	# merge the file
	merge_bed = pybedtools.BedTool()

	if merge_type == 'merge':
		#{{{ combine files into one 
		combo_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
										 'merge_beds', \
										 'tmp')

		combo_file = open(combo_file_name, 'w')
		for bed in N_list:
			in_file = open(bed.val, 'r')
			for line in in_file:
				combo_file.write(line)
			in_file.close()
		combo_file.close()
		add_tmp_file(input_type(combo_file_name, True))
		# sort the combined file
		sorted_bed = pybedtools.BedTool(combo_file_name).sort()
		add_tmp_file(input_type(sorted_bed.fn, True))

		#}}}
		merged_bed = sorted_bed.merge(**kwargs)
	elif  merge_type in ['flat','min','max'] :
		#{{{ sort each file, make list of files
		# make sure all the input files are sorted
		sorted_beds = []
		sorted_bed_files = []
		for bed in N_list:
			sorted_bed = pybedtools.BedTool(bed.val).sort()
			add_tmp_file( eval( 'gqltypes.'+ bed.name + \
				'("' + sorted_bed.fn + '",True)' ) )
			sorted_beds.append(sorted_bed)
			sorted_bed_files.append(sorted_bed.fn)

		kwargs['gql'] = True
		kwargs['i'] = sorted_bed_files
		#}}}
		x = pybedtools.BedTool()
		if merge_type == 'flat':
			try:
				merged_bed = x.multi_intersect(**kwargs)
			except pybedtools.helpers.BEDToolsError as e:
				raise ToolsException('Error in MERGE. ' +  e.msg,\
						'merge_beds')
		elif merge_type == 'min':
			kwargs['cluster'] = True
			try:
				merged_bed = x.multi_intersect(**kwargs)
			except pybedtools.helpers.BEDToolsError as e:
				raise ToolsException('Error in MERGE. ' +  e.msg,\
						'merge_beds')
		elif merge_type == 'max':
			kwargs['merge'] = True
			try:
				merged_bed = x.multi_intersect(**kwargs)
			except pybedtools.helpers.BEDToolsError as e:
				raise ToolsException('Error in MERGE. ' +  e.msg,\
						'merge_beds')
	else:
		raise ToolsException('Supported by MERGE. ' + merge_type,\
				'merge_beds')
	
	result = output_type(merged_bed.fn, True)

	add_tmp_file(result)

	return result
#}}}

#{{{ def complement_bedx(bedx, genome):
def complement_bedx(bedx, genome):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.complementable_types

	if not ( type(bedx) in allowed_types ):
		raise ToolsException('Type mismatch in COMPLEMENT. ' +\
				ident.name + ' not supported.',\
				'complement_bedx')

	kwargs = {}
	if type(genome) is str:
		try:
			test = pybedtools.chromsizes(genome)
			kwargs['genome']=genome
		except Exception as e:
			raise ToolsException(\
					'Error locating and/or retrieve genome ' + \
					genome + ' in COMPLEMENT.',\
					'complement_bedx')
	else:
		if type(genome) is gqltypes.GENOME:
			kwargs['g'] = genome.val
		else:
			raise ToolsException(\
					'Type mismatch in COMPLEMENT.  GENOME expect ' + \
					'but ' + genome.name + ' encountered.',\
					'complement_bedx')

	a = pybedtools.BedTool(bedx.val)
	r = a.complement(**kwargs)

	output_type = gqltypes.BED3

	result = output_type(r.fn, True)
	add_tmp_file(result)

	return result
#}}}

#{{{ def filter_bedx(_N_list, _opts):
def filter_bedx(_N_list, filter_opts):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types

	N_list = make_mixed_list(_N_list, allowed_types,'FILTER')

	input_types = []

	for bed in N_list:
		input_types.append(type(bed))

	output_type = ''
	if gqltypes.BED3 in input_types:
		output_type = gqltypes.BED3
	elif gqltypes.BED4 in input_types:
		output_type = gqltypes.BED4
	elif gqltypes.BED6 in input_types:
		output_type = gqltypes.BED6
	elif gqltypes.BED12 in input_types:
		output_type = gqltypes.BED12
	else:
		raise ToolsException(\
				'Output type could not be determined in FILTER.',\
				'filter_bedx')

	filter_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
									 'filter_bedx', \
									 'tmp')
	filter_bedx=output_type(filter_file_name, True)
	add_tmp_file(filter_bedx)
	filter_file = open(filter_bedx.val, 'w')
	
	for bed in N_list:
		f = open(bed.val,'r')
		bed_type =  gqltypes.source_type_map[bed.name]
		for line in f:
			cols = line.rstrip().split('\t')
			keep_line = True
			for opt in filter_opts:
				bool_string = ""
				if not opt in  bed_type.col:
					raise ToolsException(\
							'Invalid field for given filetype ' + \
							'in FILTER. ' + opt + ' and ' + bed_type.name,\
							'filter_bedx')
				opt_col = bed_type.col[opt]

				for test in filter_opts[opt]:
					try:
						if len(test)==2:
							op=test[0]
							val=test[1]
							test=cols[opt_col]

							result = ''
							if op == '=~':
								val = val.replace('"', "")
								result = str(val) in str(test)
							else:
								if type(val) is str:
									test='"'+str(test)+'"'
								result = eval(str(test) + op + str(val))

							bool_string = bool_string +	str(result)
						else:
							bool_string = bool_string + test[0]
					except Exception as e:
						raise ToolsException(\
								'Error processing ' + \
								str(val) + str(op) + str(test) + \
								' in FILTER. ' + line, \
								'filter_bedx')
				keep_line = keep_line &  eval(bool_string)
			if keep_line:
				filter_file.write(line)

	return filter_bedx
#}}}

#{{{ def sort_bedz(bedx):
def sort_bedx(bedx):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.sortable_types

	if not type(bedx) in allowed_types:
		raise ToolsException('Type mismatch in SORT. ' +\
					bedx.name + ' not supported.',\
					'cast')

	try:
		new_type = gqltypes.source_type_map[bedx.name]
		sorted_bed = pybedtools.BedTool(bedx.val).sort()
		new_file = new_type(sorted_bed.fn, True)
		add_tmp_file(new_file)
		return new_file
	except pybedtools.helpers.BEDToolsError as e:
		raise ToolsException('Error in SORT. ' + e.msg,\
					'sort')

#}}}

#{{{ def cast(bedx, new_type):
def cast(bedx, new_type):

	allowed_types = gqltypes.flat_bed_types

	if not type(bedx) in allowed_types:
		raise ToolsException('Type mismatch in CAST. ' +\
					bedx.name + ' not supported.',\
					'cast')

	if type(bedx) == gqltypes.BED12 and  \
				not new_type in \
				(gqltypes.BED3,gqltypes.BED4,gqltypes.BED6,gqltypes.BED12):
		raise ToolsException (\
				'Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type.name,\
				'cast')

	elif type(bedx) == gqltypes.BED6 and \
				not new_type in \
				(gqltypes.BED3,gqltypes.BED4,gqltypes.BED6):
		raise ToolsException (\
				'Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type.name,\
				'cast')

	elif type(bedx) == gqltypes.BED4 and \
				not new_type in \
				(gqltypes.BED3,gqltypes.BED4):
		raise ToolsException (\
				'Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type.name,\
				'cast')

	elif type(bedx) == gqltypes.BED3 and \
				not new_type  in \
				(gqltypes.BED3,gqltypes.BED3):
		raise ToolsException (\
				'Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type.name,\
				'cast')

	start_range = 0
	end_range = new_type.cols

	new_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
									 'cast', \
									 'tmp')

	new_file = new_type(new_file_name, True)
	add_tmp_file(new_file)

	in_file = open(bedx.val, 'r')
	out_file = open(new_file_name, 'w')
	for line in in_file:
		cols = line.rstrip().split('\t')
		out_file.write("\t".join(cols[start_range:end_range]) + "\n")
	in_file.close()
	out_file.close()

	return new_file
#}}}

#{{{ def mergemin_bedn(bednfile):
def mergemin_bedn(bednfile):

	allowed_types = gqltypes.BEDN

	if not ( type(bednfile) in allowed_types ):
		raise ToolsException('Type mismatch in MEREGEMIN. ' +
				bednfile.name + ' not supported.',\
				'mergemin_bedn')
	
	pybedtools.settings.KEEP_TEMPFILES=True

	#relative positions: starts 1, ends 2, name 3, score 4
	o_starts = []
	o_ends = []
	o_names = []
	o_scores = []
	o_strands = []
	
	bed_types = bednfile.types
	curr_offset = 0
	for bed_type in bed_types:
		o_starts.append(curr_offset + 1)
		o_ends.append(curr_offset + 2)
		if bed_type in (gql_types.BED6, gql_types.BED12):
			o_names.append(curr_offset + 3)
			o_scores.append(curr_offset + 4)
			o_strands.append(curr_offset + 5)
		if bed_type == gql_types.BED4:
			o_names.append(curr_offset + 3)

		curr_offset += bed_type.cols
#		if bed_type == 'BED3':
#			curr_offset += 3
#		elif bed_type == 'BED4':
#			curr_offset += 4
#		elif bed_type == 'BED6':
#			curr_offset += 6
#		elif bed_type == 'BED12':
#			curr_offset += 12 
#
	

	R_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
									 'mergemin', \
									 'tmp')

	in_file = open(bednfile.val, 'r')
	out_file = open(R_file_name, 'w')

	for line in in_file:
		cols = line.rstrip().split('\t')
		out_row = (cols[0], \
			str(max( [ int(cols[i]) for i in range(0,len(cols)) \
				if i in o_starts] )), \
			str(min( [ int(cols[i]) for i in range(0,len(cols)) \
				if i in o_ends] )), \
		)

		# if o_names is empty, then all of the beds were BED3
		if len(o_names) > 0 :
			out_row = out_row + ( \
					"::".join([ cols[i] for i in range(0,len(cols)) \
						if i in o_names]), \
					str(0), \
					random.choice([ cols[i] for i in range(0,len(cols)) \
						if i in o_strands]), \
			)
		out_file.write("\t".join(out_row) + "\n")
	in_file.close()
	out_file.close()

	new_type = gqltypes.BED6
	if len(o_names) == 0 :
		new_type = gqltypes.BED3

	#new_class = gsltypes.source_type_map(new_type)

	R = new_type(R_file_name, True)

	add_tmp_file(R)

	return R
#}}}

#{{{ def plot_val(ident, filename):
def plot_val(ident, filename):

	allowed_types = gqltypes.plotable_types

	if not ( type(ident) in allowed_types ):
		raise ToolsException('Type mismatch in PLOT. ' +\
				ident.name + ' not supported.',\
				'plot_val')
	
	ident.plot(filename)
#}}}

#{{{ def print_val(ident, num):
def print_val(ident, num):

	allowed_types = gqltypes.printable_types

	if not ( type(ident) in allowed_types ):
		raise ToolsException('Type mismatch in PRINT. ' +\
				ident.name + ' not supported.',\
				'print_val')
	
	ident.print_val(num)
#}}}

#{{{ def print_file(fname, num):
def print_file(fname, num):
	if not os.path.isfile(fname):
		raise ToolsException('File does not exist in PRINT: ' + fname,\
				'print_file')

	f = open(fname, 'r')
	line_num = 0
	for line in f:
		if num == -1:
			print line,
		else:
			if line_num < num:
				print line,
				line_num+=1;
			else:
				break
	f.close()
#}}}

#{{{ def save_file(ident, path):
def save_file(ident, path):
	allowed_types = gqltypes.saveable_types

	if not ( type(ident) in allowed_types ):
		raise ToolsException('Type mismatch in SAVE. ' +
				bed.name + ' not supported.',\
				'save_file')

	shutil.copy(ident.val, path)
#}}}

#{{{ def load_file(file_path, filetype_name):
def load_file(file_path, filetype_name):

	# local files are not temp files, but remote files are
	is_remote = False

	return_files = []
	return_labels = []

	# attempt to get the files from the local path
	files = glob.glob(file_path)

	if len(files) == 0:
		# if nothing at the local path, then see if it is a remote path
		# if so, then fetch the files, store at temp path, and place 
		# the temp file path in the files list
		is_remote = True
		#url = 'http://localhost/cgi-bin/name.py?path=' + file_path

		# retrieve the path from the name server 
		try:
			url = config['fileserver'] + 'name.py?path=' + file_path
			json_response = urllib.urlopen(url)
			s = json_response.read()
			remote_paths = json.loads(s)
			json_response.close()
		except Exception as e:
			raise ToolsException ('Error retrieving file',\
					'load_file')

		# fetch remote files
		for remote_path in remote_paths:
			tmp_file_path = get_temp_file_name(pybedtools.get_tempdir(), \
											   'load', \
											   'tmp')
			# first value is the label
			return_labels.append(remote_path[0])
			# second is the path
			urllib.urlretrieve(remote_path[1], tmp_file_path)
			files.append(tmp_file_path)

		# if there is not remote file at this url, then raise
		if len(remote_paths) == 0:
			raise ToolsException (\
					'No file(s) not found at ' + file_path, 'load_file')

	for f in files:
		if (filetype_name == 'auto') :
			type_found = False
			# loops through the types to see which one matches
			for source_type in gqltypes.source_types:
				if source_type.test_filetype(f):
					type_found = True
					# if the files is remote, then the temp paramater is true
					# otherwise it is false
					new_file = source_type(f, is_remote)

					if is_remote:
						add_tmp_file(new_file)
					else:
						# remote labels were collected previously 
						return_labels.append(os.path.basename(f))

					return_files.append(new_file)
			if not type_found:
				raise ToolsException('Unknown filetype for:' + f,'load_file')
		else:
			source_type = gqltypes.source_type_map[filetype_name]
			if source_type.test_filetype(f):
				# if the files is remote, then the temp paramater is true
				# otherwise it is false
				new_file = source_type(f, is_remote)
				if is_remote:
					add_tmp_file(new_file)
				else:
					# remote labels were collected previously 
					return_labels.append(os.path.basename(f))

				return_files.append(new_file)
			else:
				raise ToolsException('Filetype mismatch:' + f + \
						" does not appear to be " + filetype_name,
						'load_file')

	if len(return_files) == 1:
		return return_files[0]
	else:
		return gqltypes.BEDL(return_files, return_labels)
#}}}

#{{{def count(ident):
def count(ident):
	allowed_types = gqltypes.countable_types

	if not ( type(ident) in allowed_types ):
		raise ToolsException('Type mismatch in COUNT. ' +
				bedx.name + ' not supported.', 'count')

	return ident.count()
#}}}

#{{{ def file_len(fname):
def file_len(fname):
	return bufcount(fname)
# http://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python
def simplecount(fname):
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
	return i + 1

def mapcount(filename):
	f = open(filename, "r+")
	buf = mmap.mmap(f.fileno(), 0)
	lines = 0
	readline = buf.readline
	while readline():
		lines += 1
	return lines


def bufcount(filename):
	f = open(filename)                  
	lines = 0
	buf_size = 1024 * 1024
	read_f = f.read # loop optimization

	buf = read_f(buf_size)
	while buf:
		lines += buf.count('\n')
		buf = read_f(buf_size)

	return lines
#}}}

#{{{ def hilbert_curve_matrix(_N_list, 
def hilbert_curve_matrix(_N_list, \
						 _N_labels, \
						 mods):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.hilbertable_types

	(N_list, N_label) = make_mixed_list_with_labels(_N_list, \
													_N_labels, \
													allowed_types,\
													'HILBERT')


	chrom = 'genome'
	genome = ''
	dim = 0

	if 'chrom' in mods:
		chrom = mods['chrom']
	
	if 'genome' not in mods:
		raise ToolsException('Error in HILBERT. No genome or genome file ' + \
				'provided.',\
				'hilbert_curve_matrix')
	else:
		if type(mods['genome']) is str:
			genome = mods['genome']
		else:
			genome = mods['genome'].val

	if 'dimension' not in mods:
		raise ToolsException('Error in HILBERT. No dimension provided.',\
				'hilbert_curve_matrix')
	else:
		dim = mods['dimension']

	matrix_list = []
	for N in N_list:
		try:
			hm = scurgen.hilbert.HilbertMatrix(N.val,\
											   genome,\
											   chrom,\
											   int(dim))
			hm.norm_by_total_intervals()
			matrix_list.append(gqltypes.NUMMATRIX(hm.matrix,[]))

		except Exception as e:
			raise ToolsException('Error in HILBERT. ',\
					'hilbert_curve_matrix')

	if len(matrix_list) == 1:
		return matrix_list[0]
	else:
		return gqltypes.LIST(matrix_list,N_label)
#}}}

#{{{ def make_mixed_list_with_labels(_N_list, \
def make_mixed_list_with_labels(_N_list, \
								_N_labels,
								allowed_types,
								calling_method):

	N_list = []
	N_label = []
	for i in range(0, len(_N_list)):
		bedx = _N_list[i]
		if not (type(bedx) in allowed_types):
			raise ToolsException('Type mismatch in '+ calling_method + '. '+
					bedx.name + ' not supported.',
					'make_mixed_list_with_labels')
		if type(bedx) == gqltypes.BEDL:
			for j in range(0, len(bedx.val)):
				N_list.append(bedx.val[j])
				N_label.append(bedx.labels[j])
		else:
			N_list.append(bedx)
			N_label.append(_N_labels[i])

	return (N_list, N_label)
#}}}

#{{{ def make_mixed_list(_N_list, \
def make_mixed_list(_N_list, \
					allowed_types,
					calling_method):

	N_list = []
	for i in range(0, len(_N_list)):
		bedx = _N_list[i]
		if not (type(bedx) in allowed_types):
			raise ToolsException('Type mismatch in '+ calling_method + '. '+
					bedx.name + ' not supported.',
					'make_mixed_list')
		if type(bedx) == gqltypes.BEDL:
			for j in range(0, len(bedx.val)):
				N_list.append(bedx.val[j])
		else:
			N_list.append(bedx)

	return N_list
#}}}
