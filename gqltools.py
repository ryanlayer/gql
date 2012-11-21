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

tmp_files = []

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
		raise Exception('Unmached sizes in intersection')


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
													allowed_types)

	(M_list, M_label) = make_mixed_list_with_labels(_M_list, \
													_M_labels, \
													allowed_types)

	NM_matrix = []
	for N in N_list:
		N_bed = pybedtools.BedTool( N.val )
		NM_list = []
		for M in M_list:
			M_bed = pybedtools.BedTool( M.val )
			try:
				NM_bed = N_bed.intersect(b=M_bed,wo=True)
			except pybedtools.helpers.BEDToolsError as e:
				raise Exception('Error in INTERSECT. ' + e.msg )

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
													allowed_types)

	(M_list, M_label) = make_mixed_list_with_labels(_M_list, \
													_M_labels, \
													allowed_types)

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
				raise Exception('Error in JACCARD. ' + e.msg )

			num = gqltypes.NUM(r['jaccard'])
			num_list.append(num)
		num_matrix.append(num_list)

	return gqltypes.NUMMATRIX(num_matrix,[N_label,M_label])
#}}}
	
#{{{ def unary_intersect_beds(ordered_bed_list, bed_labels):
def unary_intersect_beds(_N_list, _N_labels):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types

	(N_list, N_labels) = make_mixed_list_with_labels(_N_list,
													 _N_labels,
													 allowed_types)

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
			raise Exception('Error in INTERSECT. ' + e.msg )

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

	N_list = make_mixed_list(_N_list, allowed_types)

	if not (type(bedx) in gqltypes.flat_bed_types):
		raise Exception('Type mismatch in SUBTRACT. ' + \
				bedx.name + ' not supported.')

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
			raise Exception('Error in SUBTRACT. ' +  e.msg )

		AB = A.__class__(AB_bed.fn, True)
		add_tmp_file(AB)

		bed_queue.appendleft(AB)

	return bed_queue.popleft()
#}}}

#{{{ def merge_beds(N_list, merge_opts):
def merge_beds(merge_type, _N_list, merge_opts):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types

	N_list = make_mixed_list(_N_list, allowed_types)

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
			raise Exception('Invalid option in MERGE. ' + \
						merge_opt + ' not supported.')

		if merge_opt == 'score':
			if not ( merge_opts[ merge_opt ] in score_functions ) :
				raise Exception('SCORE funciton not supported by MERGE. ' + \
						merge_opts[ merge_opt ])
			else:
				kwargs[ valid_args[ merge_opt ] ] = \
						score_functions[ merge_opts[ merge_opt ] ]
		elif merge_opt == 'stranded':
			if (gqltypes.BED3 in input_types ) or \
				( gqltypes.BED4 in input_types) or \
				( gqltypes.BED5 in input_types)  :
				raise Exception('Type mismatch in MERGE. Cannot match by ' +
					'strand with givne input types')
			kwargs[ valid_args[ merge_opt ] ] = True

		elif (merge_opt == 'distance'):
			if merge_type == 'flat':
				raise Exception('DISTANCE not supported for MERGEFLAT')
			elif merge_type == 'min':
				raise Exception('DISTANCE not supported for MERGEMIN')
			elif merge_type == 'max':
				raise Exception('DISTANCE not supported for MERGEMAX')
			else:
				kwargs[ valid_args[ merge_opt ] ] = merge_opts[ merge_opt ]

		elif (merge_opt == 'name'):
			if merge_opts[ merge_opt ] == 'COLLAPSE':
				kwargs[ valid_args[ merge_opt ] ] = True
			else :
				raise Exception('NAME funciton not supported by MERGE. ' + \
						merge_opts[ merge_opt ])
	

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
				raise Exception('Error in MERGE. ' +  e.msg )
		elif merge_type == 'min':
			kwargs['cluster'] = True
			try:
				merged_bed = x.multi_intersect(**kwargs)
			except pybedtools.helpers.BEDToolsError as e:
				raise Exception('Error in MERGE. ' +  e.msg )
		elif merge_type == 'max':
			kwargs['merge'] = True
			try:
				merged_bed = x.multi_intersect(**kwargs)
			except pybedtools.helpers.BEDToolsError as e:
				raise Exception('Error in MERGE. ' +  e.msg )
	else:
		raise Exception('Supported by MERGE. ' + merge_type)
	
	result = output_type(merged_bed.fn, True)

	add_tmp_file(result)

	return result
#}}}

#{{{ def def filter_bedx(_N_list, _opts):
def filter_bedx(_N_list, filter_opts):
	pybedtools.settings.KEEP_TEMPFILES=True

	allowed_types = gqltypes.bed_types

	N_list = make_mixed_list(_N_list, allowed_types)

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
		raise Exception('Output type could not be determined in FOREACH.')

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
					raise Exception('Invalid field for given filetype ' +
							'in FOREACH. ' + opt + ' and ' + bed_type.name)
				opt_col = bed_type.col[opt]

				for test in filter_opts[opt]:
					if len(test)==2:
						op=test[0]
						val=test[1]
						test=cols[opt_col]
						if type(val) is str:
							test='"'+str(test)+'"'
						result = eval(str(test) + op + str(val))
						bool_string = bool_string +str(result)
					else:
						bool_string = bool_string + test[0]
				keep_line = keep_line &  eval(bool_string)
			if keep_line:
				filter_file.write(line)

	return filter_bedx
#}}}

#{{{ def cast(bedx, new_type):
def cast(bedx, new_type):

	allowed_types = gqltypes.flat_bed_types

	if not type(bedx) in allowed_types:
		raise Exception('Type mismatch in CAST. ' +
					bedx.name + ' not supported.')

	if type(bedx) == gqltypes.BED12 and  \
				not new_type in \
				(gqltypes.BED3,gqltypes.BED4,gqltypes.BED6,gqltypes.BED12):
		raise Exception ('Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type.name)

	elif type(bedx) == gqltypes.BED6 and \
				not new_type in \
				(gqltypes.BED3,gqltypes.BED4,gqltypes.BED6):
		raise Exception ('Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type.name)

	elif type(bedx) == gqltypes.BED4 and \
				not new_type in \
				(gqltypes.BED3,gqltypes.BED4):
		raise Exception ('Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type.name)

	elif type(bedx) == gqltypes.BED3 and \
				not new_type  in \
				(gqltypes.BED3,gqltypes.BED3):
		raise Exception ('Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type.name)

	start_range = 0
	end_range = new_type.cols

#	if new_type == 'BED12':
#		end_range = 13
#	elif new_type == 'BED6':
#		end_range = 6 
#	elif new_type == 'BED4':
#		end_range = 4 
#	elif new_type == 'BED3':
#		end_range = 3 

	new_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
									 'cast', \
									 'tmp')

	#new_class = gqltypes.source_type_map[new_type]

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
		raise Exception('Type mismatch in MEREGEMIN. ' +
				bednfile.name + ' not supported.')
	
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

#{{{ def print_val(ident, num):
def print_val(ident, num):

	allowed_types = gqltypes.printable_types

	if not ( type(ident) in allowed_types ):
		raise Exception('Type mismatch in PRINT. ' +\
				ident.name + ' not supported.')
	
	ident.print_val(num)
#}}}

#{{{ def print_file(fname, num):
def print_file(fname, num):
	if not os.path.isfile(fname):
		raise Exception('File does not exist in PRINT: ' + fname)

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
		raise Exception('Type mismatch in SAVE. ' +
				bed.name + ' not supported.')

	shutil.copy(ident.val, path)
#}}}

#{{{ def load_file(file_path, filetype_name):
def load_file(file_path, filetype_name):

	files = glob.glob(file_path)

	if len(files) == 0:
		raise Exception ('No file(s) not found at ' + file_path, 'load')

	return_files = []
	return_labels = []

	for f in files:
		if (filetype_name == 'auto') :
			type_found = False
			for source_type in gqltypes.source_types:
				if source_type.test_filetype(f):
					type_found = True
					return_files.append(source_type(f, False))
					return_labels.append(os.path.basename(f))
			if not type_found:
				raise Exception('Unknown filetype for:' + f)
		else:
			source_type = gqltypes.source_type_map[filetype_name]
			if source_type.test_filetype(f):
				return_files.append(source_type(f, False))
				return_labels.append(f)
			else:
				raise Exception('Filetype mismatch:' + f + \
						" does not appear to be " + filetype_name)

	if len(return_files) == 1:
		return return_files[0]
	else:
		return gqltypes.BEDL(return_files, return_labels)
#}}}

#{{{def count(ident):
def count(ident):
	allowed_types = gqltypes.countable_types

	if not ( type(ident) in allowed_types ):
		raise Exception('Type mismatch in COUNT. ' +
				bedx.name + ' not supported.')

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

#{{{ def make_mixed_list_with_labels(_N_list, \
def make_mixed_list_with_labels(_N_list, \
								_N_labels,
								allowed_types):

	N_list = []
	N_label = []
	for i in range(0, len(_N_list)):
		bedx = _N_list[i]
		if not (type(bedx) in allowed_types):
			raise Exception('Type mismatch in INTERSECT. ' +
					bedx.name + ' not supported.')
		if type(bedx) == gqltypes.BEDL:
			for j in range(0, len(bedx.val)):
				N_list.append(bedx.val[j])
				N_label.append(bedx.labels[j])
		else:
			N_list.append(bedx)
			N_label.append(_N_labels[i])

	return (N_list, N_label)
#}}}

#{{{ def make_mixed_list_with_labels(_N_list, \
def make_mixed_list(_N_list, \
					allowed_types):

	N_list = []
	for i in range(0, len(_N_list)):
		bedx = _N_list[i]
		if not (type(bedx) in allowed_types):
			raise Exception('Type mismatch in INTERSECT. ' +
					bedx.name + ' not supported.')
		if type(bedx) == gqltypes.BEDL:
			for j in range(0, len(bedx.val)):
				N_list.append(bedx.val[j])
		else:
			N_list.append(bedx)

	return N_list
#}}}
