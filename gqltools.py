import re
import gqlfiletypes
import pybedtools
import random
import sys
import os.path
import os
import linecache
from collections import deque
import shutil

tmp_files = []

def add_tmp_file(tmp):
	tmp_files.append(tmp)

def clear_tmp_files():
	for tmp_file in tmp_files:
		if tmp_file['tmp']:
			os.remove(tmp_file['val'])
		

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
									 'intersect_beds', \
									 'tmp')

	offset = 0

	if A['type'] == 'BED3':
		offset = 3
	elif A['type'] == 'BED6':
		offset = 6
	if A['type'] == 'BED12':
		offset = 12 

	curr_line = 1

	out_file = open(R_file_name, 'w')
	in_file = open(AB['val'], 'r')
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

	R = {'val':R_file_name, 'type':'BED6', 'tmp':True }

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

		in_file = open(AB['val'], 'r')

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
									 'intersect_beds', \
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
		#print out_line
		out_file.write(out_line + '\n')

	out_file.close()

	R = {'val':R_file_name, 'type':'BEDN', 'tmp':True }

	add_tmp_file(R)

	return R
#}}}
	
#{{{ def intersect_beds(ordered_bed_list):
def intersect_beds(ordered_bed_list):

	allowed_types = ('BED3', 'BED6', 'BED12')

	for bed in ordered_bed_list:
		if not ( bed['type'] in allowed_types ):
			raise Exception('Type mismatch in intersect_beds. ' +
					bed['type'] + ' not supported.')
	
	pybedtools.settings.KEEP_TEMPFILES=True

	bed_queue = deque(ordered_bed_list)
	out_stack = []
	while ( len(bed_queue) > 1 ):
		A = bed_queue.popleft()
		A_bed = pybedtools.BedTool( A['val'] )

		B = bed_queue.popleft()
		B_bed = pybedtools.BedTool( B['val'] )

		AB_bed = A_bed.intersect(b=B_bed,wo=True)
		AB = {'val':AB_bed.fn, 'type':'BEDN', 'tmp':True }

		add_tmp_file(AB)

		R = get_intersect_result( [A, B, AB] )

		bed_queue.appendleft(R)
		out_stack.append( [A, B, AB] )

	R = merge_bed_stack(out_stack)

	return R
#}}}

#{{{ def subtract_beds(ordered_bed_list):
def subtract_beds(ordered_bed_list):

	allowed_types = ('BED3', 'BED6', 'BED12')

	for bed in ordered_bed_list:
		if not ( bed['type'] in allowed_types ):
			raise Exception('Type mismatch in intersect_beds. ' +
					bed['type'] + ' not supported.')
	
	pybedtools.settings.KEEP_TEMPFILES=True

	bed_queue = deque(ordered_bed_list)
	while ( len(bed_queue) > 1 ):
		A = bed_queue.popleft()
		A_bed = pybedtools.BedTool( A['val'] )

		B = bed_queue.popleft()
		B_bed = pybedtools.BedTool( B['val'] )

		AB_bed = A_bed.intersect(b=B_bed,v=True)
		AB = {'val':AB_bed.fn, 'type':'BEDN', 'tmp':True }

		add_tmp_file(AB)

		bed_queue.appendleft(AB)

	return bed_queue.popleft()
#}}}

#{{{ def merge_min(bednfile):
def merge_min(bednfile):

	allowed_types = ('BEDN')

	if not ( bednfile['type'] in allowed_types ):
		raise Exception('Type mismatch in intersect_beds. ' +
				bednfile['type'] + ' not supported.')
	
	pybedtools.settings.KEEP_TEMPFILES=True

	types = bednfile['types']

	
#}}}

#{{{ def print_file(ident):
def print_file(ident):
	f = open(ident['val'], 'r')
	for line in f:
		print line
	f.close()
#}}}

#{{{ def save_file(ident, path):
def save_file(ident, path):
	shutil.copy(ident['val'], path)
#}}}

#{{{ def verify_filetype(file_path, filetype_name):
def verify_filetype(file_path, filetype_name):

	f = open(file_path, 'r')
	#trash the first line, unless there is only one line
	line_1 = f.readline()
	test_line = f.readline()
	f.close()

	if test_line == '':
		test_line = line_1 

	line_list = test_line.rstrip().split('\t')

	filetype_def = gqlfiletypes.filetypes[filetype_name]

	# test to make sure the number of cols matches
	if ( len(line_list) == len(filetype_def) ) :
		for i in range( len(line_list) ):	

			# test each 
			if re.match(filetype_def[i], line_list[i]) == None:
				return False
	else:
		return False
	return True
#}}}
