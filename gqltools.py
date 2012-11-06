import re
import gqlfiletypes
import gqltypes
import pybedtools
import random
import sys
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

	offset = 0

	if A.name == 'BED3':
		offset = 3
	elif A.name == 'BED6':
		offset = 6
	if A.name == 'BED12':
		offset = 12 

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

	#R = {'val':R_file_name, 'type':'BED6', 'tmp':True }
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

	#R = {'val':R_file_name, 'type':'BEDN', 'tmp':True }
	R = gqltypes.BEDN(R_file_name, True)

	add_tmp_file(R)

	return R
#}}}

#{{{ def binary_intersect_beds(ordered_bed_list_A, ordered_bed_list_B):
def binary_intersect_beds(ordered_bed_list_N, \
						  label_list_N, \
						  ordered_bed_list_M, \
						  label_list_M):

	allowed_types = ('BED3', 'BED6', 'BED12')

	for bed in ordered_bed_list_N + ordered_bed_list_M:
		if not ( bed.name in allowed_types ):
			raise Exception('Type mismatch in INTERSECT. ' +
					bed.name + ' not supported.')

	pybedtools.settings.KEEP_TEMPFILES=True

	NM_list = []
	for N in ordered_bed_list_N:
		N_bed = pybedtools.BedTool( N.val )
		M_list = []
		for M in ordered_bed_list_M:
			M_bed = pybedtools.BedTool( M.val )

			NM_bed = N_bed.intersect(b=M_bed,wo=True)
			NM = gqltypes.BEDN(NM_bed.fn,True)
			NM.types = [N.name,M.name]
			#NM = {'val':NM_bed.fn, \
					#'type':'BEDN', \
					#'types':[N['type'],M['type']], \
					#'tmp':True }
			add_tmp_file(NM)

			M_list.append(NM)
		NM_list.append(M_list)

	#return {'val':NM_list, \
			#'labels':[label_list_N,label_list_M], \
			#'type': 'BEDM'}
	return gqltypes.BEDM(NM_list,[label_list_N,label_list_M])
#}}}
	
#{{{ def unary_intersect_beds(ordered_bed_list, bed_labels):
def unary_intersect_beds(ordered_bed_list, bed_labels):

	allowed_types = ('BED3', 'BED6', 'BED12')

	bed_types = []
	for bed in ordered_bed_list:
		bed_types = bed_types + [ bed.name ]
		if not ( bed.name in allowed_types ):
			raise Exception('Type mismatch in INTERSECT. ' +
					bed.name + ' not supported.')
	
	pybedtools.settings.KEEP_TEMPFILES=True

	bed_queue = deque(ordered_bed_list)
	out_stack = []
	while ( len(bed_queue) > 1 ):
		A = bed_queue.popleft()
		A_bed = pybedtools.BedTool( A.val )

		B = bed_queue.popleft()
		B_bed = pybedtools.BedTool( B.val )

		#intersect the top two bed files in the stack
		AB_bed = A_bed.intersect(b=B_bed,wo=True)
		#AB = {'val':AB_bed.fn, 'type':'BEDN', 'tmp':True }
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
	R.labels = bed_labels
	R.types = bed_types

	return R
#}}}

#{{{ def subtract_beds(ordered_bed_list):
def subtract_beds(ordered_bed_list):

	allowed_types = ('BED3', 'BED6', 'BED12')

	for bed in ordered_bed_list:
		if not ( bed.name in allowed_types ):
			raise Exception('Type mismatch in SUBTRACT. ' +
					bed.name + ' not supported.')
	
	pybedtools.settings.KEEP_TEMPFILES=True

	bed_queue = deque(ordered_bed_list)
	while ( len(bed_queue) > 1 ):
		A = bed_queue.popleft()
		A_bed = pybedtools.BedTool( A.val )

		B = bed_queue.popleft()
		B_bed = pybedtools.BedTool( B.val )

		AB_bed = A_bed.intersect(b=B_bed,v=True)
		#AB = {'val':AB_bed.fn, 'type':A['type'], 'tmp':True }
		AB = A.__class__(AB_bed.fn, True)

		add_tmp_file(AB)

		bed_queue.appendleft(AB)

	return bed_queue.popleft()
#}}}

#{{{ def merge_beds(bed_list, merge_opts):
def merge_beds(bed_list, merge_opts):
	pybedtools.settings.KEEP_TEMPFILES=True

	#{{{ parameter type checking
	allowed_types = (gqltypes.BED3, gqltypes.BED6, gqltypes.BED12)

	for bed in bed_list:
		if not ( bed.name in allowed_types ):
			raise Exception('Type mismatch in MERGE. ' +
					bed.name + ' not supported.')
	
	all_beds_match = True
	for i in range(0,len(bed_list) - 1):
		all_beds_match = all_beds_match and \
			(bed_list[i]).name == (bed_list[i+1]).name

	if not all_beds_match:
		raise Exception('Type mismatch in MERGE. All inputs must be the ' + \
				'same type.')
	#}}}

	input_type = (bed_list[0]).__class__

	#{{{ combine files into one 
	combo_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
									 'merge_beds', \
									 'tmp')

	combo_file = open(combo_file_name, 'w')
	for bed in bed_list:
		in_file = open(bed.val, 'r')
		for line in in_file:
			combo_file.write(line)
		in_file.close()
	combo_file.close()
	#add_tmp_file({'val':combo_file_name, 'type':input_type, 'tmp':True})
	add_tmp_file(input_type(combo_file_name, True))
	#}}}

	
	# sort the combined file
	sorted_bed = pybedtools.BedTool(combo_file_name).sort()
	#add_tmp_file({'val':sorted_bed.fn, 'type':input_type, 'tmp':True})
	add_tmp_file(input_type(sorted_bed.fn, True))


	# Parse input arguments and add/modify default argumetns
	# Default args
	valid_args = {'distance':'d', \
				  'score':'scores', \
				  'stranded':'s'}

	kwargs = {}
	for merge_opt in merge_opts:
		if not ( merge_opt in valid_args ):
			raise Exception('Invalid option in MERGE. ' + \
						merge_opt + ' not supported.')
		if (merge_opt == 'score') and (input_type in ['BED3','BED4']) :
			raise Exception('Type mismatch in MERGE. Cannot aggregare ' + \
					'scores with for type:' + input_type)

		if (merge_opt == 'stranded') and \
				(input_type in ['BED3','BED4','BED5']) :
			raise Exception('Type mismatch in MERGE. Cannot aggregare ' + \
					'scores with for type:' + input_type)

		kwargs[ valid_args[ merge_opt ] ] = merge_opts[ merge_opt ]

	# merge the file
	merged_bed = sorted_bed.merge(**kwargs)

	resul = input_type(merged_bed.fn, True)

	add_tmp_file(result)

	return result
#}}}

#{{{ def cast(bedx, new_type):
def cast(bedx, new_type):

	allowed_types = ('BED3', 'BED6', 'BED12')

	if not bedx.name in allowed_types:
		raise Exception('Type mismatch in CAST. ' +
					bedx.name + ' not supported.')

	if bedx.name == 'BED12' and not new_type in ['BED3', 'BED6', 'BED12']:
		raise Exception ('Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type)
	elif bedx.name == 'BED6' and not new_type in ['BED3', 'BED6']:
		raise Exception ('Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type)
	elif bedx.name == 'BED3' and not new_type in ['BED3']:
		raise Exception ('Type mismatch in CAST. Cannot cast from ' + \
				bedx.name + ' to ' + new_type)

	start_range = 0
	end_range = 1

	if new_type == 'BED12':
		end_range = 13
	elif new_type == 'BED6':
		end_range = 6 
	elif new_type == 'BED3':
		end_range = 3 

	new_file_name = get_temp_file_name(pybedtools.get_tempdir(), \
									 'cast', \
									 'tmp')

	new_class = gsltypes.source_type_map(new_type)

	new_file = new_class(new_file_name, True)
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

	allowed_types = ('BEDN')

	if not ( bednfile.name in allowed_types ):
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
		if bed_type != 'BED3':
			o_names.append(curr_offset + 3)
			o_scores.append(curr_offset + 4)
			o_strands.append(curr_offset + 5)

		if bed_type == 'BED3':
			curr_offset += 3
		elif bed_type == 'BED6':
			curr_offset += 6
		elif bed_type == 'BED12':
			curr_offset += 12 

	

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

	new_type = 'BED6'
	if len(o_names) == 0 :
		new_type = 'BED3'

	new_class = gsltypes.source_type_map(new_type)

	R = new_class(R_file_name, True)

	add_tmp_file(R)

	return R
#}}}

#{{{ def print_bedx(ident):
def print_bedx(bedx):

	allowed_types = ['BED3', 'BED6', 'BED12', 'BEDN', 'BEDM']

	if not ( bedx.name in allowed_types ):
		raise Exception('Type mismatch in MEREGEMIN. ' +
				bedx.name + ' not supported.')
	

	if bedx.name in ('BED3', 'BED6', 'BED12', 'BEDN'):
		print_file(bedx.val)
	elif bedx.name == 'BEDM':
		for i in range (0, len( (bedx.labels)[0] ) ):
			for j in range (0, len( (bedx.labels)[1] ) ):
				print  bedx.labels[0][i] + "::" + bedx.labels[1][j]
				print_file(bedx.val[i][j].val)
#}}}

#{{{ def print_file(fname):
def print_file(fname):
	f = open(fname, 'r')
	for line in f:
		print line,
	f.close()
#}}}

#{{{ def save_file(ident, path):
def save_file(ident, path):
	shutil.copy(ident.val, path)
#}}}

#{{{ def load_file(file_path, filetype_name):
def load_file(file_path, filetype_name):

	# make sure file exists
	if ( not os.path.isfile(file_path) ):
		raise Exception ('file not found ' + file_path, 'load')

	f = open(file_path, 'r')
	#trash the first line, unless there is only one line
	line_1 = f.readline()
	test_line = f.readline()
	f.close()

	if test_line == '':
		test_line = line_1 

	line_list = test_line.rstrip().split('\t')

	if (filetype_name == 'auto') :
		for source_type in gqltypes.source_types:
			if source_type.test_filetype(file_path):
				return source_type(file_path, False)
				#return {'val':file_path, 'type':source_type.name, 'tmp':False}

		raise Exception('Unknown filetype :' + file_path)

	source_type = gqltypes.source_type_map[filetype_name]
	if source_type.test_filetype(file_path):
		return source_type(file_path, False)
		#return {'val':file_path, 'type':source_type.name, 'tmp':False}
	else:
		raise Exception('Filetype mismatch:' + file_path + \
				" does not appear to be " + filetype_name)
#}}}

#{{{def count(bed):
def count(bed):
	allowed_types = ['BED3', 'BED6', 'BED12', 'BEDN', 'BEDM']

	if not ( bed.name in allowed_types ):
		raise Exception('Type mismatch in INTERSECT. ' +
				bed.name + ' not supported.')


	if bed.name == 'BEDM':
		print "\t" + "\t".join( bed.labels[1] )
		for i in range (0, len( (bed.labels)[0] ) ):
			count_string = bed.labels[0][i]
			for j in range (0, len( (bed.labels)[1] ) ):
				count_string = count_string + '\t' + \
					str(file_len(bed.val[i][j].val))
			print count_string
	elif bed.name in ['BED3','BED6','BED12','BEDN']:
		print str( file_len(bed.val) )
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
