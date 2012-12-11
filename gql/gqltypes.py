import re
import gqltools
import numpy as np
from matplotlib import pyplot as plt

chr_re = r'chr.+$'
string_re = r'.*$'
float_re = r'-?[0-9]+(\.[0-9]*)?'
one_digit_re = r'[0-9]+$'
cs_digits_re = r'[0-9]+(,[0-9]+)*'
strand_re = r'\+|\-'
rgb_re = r'[0-9]+,[0-9]+,[0-9]+$'


#{{{ class EnvElement(object):
class EnvElement(object):
	def __init__(self):
		pass
#}}}

#{{{class Lineno(EnvElement):
class Lineno(EnvElement):
	def __init__(self):
		pass
#}}}

#{{{class SourceFile(object):
class SourceFile(object):
	file_format = []
	@classmethod
	def print_file_format(self):
		print self.file_format
	@classmethod
	def test_filetype(self, file_path):
		f = open(file_path, 'r')
		#trash the first line, unless there is only one line
		line_1 = f.readline()
		test_line = f.readline()
		f.close()

		if test_line == '':
			test_line = line_1 

		line_list = test_line.rstrip().split('\t')

		# test to make sure the number of cols matches
		if ( len(line_list) == len(self.file_format) ) :
			for i in range( len(line_list) ):	
				# test each 
				if re.match(self.file_format[i], line_list[i]) == None:
					return False
		else:
			return False
		return True

	def count(self):
		return NUM(gqltools.file_len(self.val))

	def print_val(self,num):
		gqltools.print_file(self.val, num)

	def __init__(self,val,tmp):
		self.val = val;
		self.tmp = tmp;

	def __str__(self):
		return "(" + self.val + "," + str(self.tmp) + ")"
#}}}

#{{{class BED3(EnvElement,SourceFile):
class BED3(EnvElement,SourceFile):
	name = 'BED3'
	cols=3
	col = {'chrom':0,
		   'start':1,
		   'end':2,
	}
	# each entry represents a column
	file_format = [ chr_re, #chrom
					one_digit_re, #start
					one_digit_re, #end
	]
	def __init__(self,val,tmp):
		SourceFile.__init__(self,val,tmp)
#}}}

#{{{class BED4(EnvElement,SourceFile):
class BED4(EnvElement,SourceFile):
	name = 'BED4'
	cols=4
	col = {'chrom':0,
		   'start':1,
		   'end':2,
		   'name':3,
	}
	# each entry represents a column
	file_format = [ chr_re, #chrom
					one_digit_re, #start
					one_digit_re, #end
					string_re,		#name
	]
	def __init__(self,val,tmp):
		SourceFile.__init__(self,val,tmp)
#}}}

#{{{ class BED6(EnvElement,SourceFile):
class BED6(EnvElement,SourceFile):
	name = 'BED6'
	cols=6
	col = {'chrom':0,
		   'start':1,
		   'end':2,
		   'name':3,
		   'score':4,
		   'strand':5,
	}
	file_format = [ chr_re,		#chrom
					one_digit_re,	#start
					one_digit_re,	#end
					string_re,		#name
					float_re,		#score
					strand_re,		#strand
	]
	def __init__(self,val,tmp):
		SourceFile.__init__(self,val,tmp)
#}}}

#{{{ class BED12(EnvElement,SourceFile):
class BED12(EnvElement,SourceFile):
	name = 'BED12'
	cols=12
	col = {'chrom':0,
		   'start':1,
		   'end':2,
		   'name':3,
		   'score':4,
		   'strand':5,
		   'thickStart':6,
		   'thickEnd':7,
		   'itemRgb':8,
		   'blockCount':9,
		   'blockSizes':10,
		   'blockStarts':11,
	}
	file_format = [ chr_re,		#chrom
					one_digit_re,	#start
					one_digit_re,	#end
					string_re,		#name
					float_re,		#score
					strand_re,		#strand
					one_digit_re,	#thickstart
					one_digit_re,	#thickend
					cs_digits_re,	#rgb
					one_digit_re,	#blockcount
					cs_digits_re,	#blocksizes
					cs_digits_re,	#blockstarts
	]
	def __init__(self,val,tmp):
		SourceFile.__init__(self,val,tmp)
#}}}

#{{{ class GENOME(EnvElement,SourceFile):
class GENOME(EnvElement,SourceFile):
	name = 'GENOME'
	file_format = [	chr_re, #chrom
					one_digit_re, #length
	]
	def __init__(self,val,tmp):
		SourceFile.__init__(self,val,tmp)
#}}}

#{{{ class BEDN(EnvElement):
class BEDN(EnvElement):
	name = 'BEDN'
	def __init__(self,val,tmp):
		self.val = val
		self.tmp = tmp
		self.labels = []
		self.types = []
	def __str__(self):
		return "(" + self.val + "," + \
					 str(self.tmp) + "," + \
					 str(self.labels) + \
					 str(self.types) + \
					 ")"

	def count(self):
		return NUM(gqltools.file_len(self.val))

	def print_val(self,num):
		gqltools.print_file(self.val, num)

#}}}

#{{{ class BEDM(EnvElement):
class BEDM(EnvElement):
	name = 'BEDM'
	def __init__(self,val,labels):
		self.val = val
		self.labels = labels

	def count(self):
		count_m = []
		for i in range (0, len( (self.labels)[0] ) ):
			count_r = [ gqltools.file_len(x.val) for x in self.val[i]]
			count_m.append(count_r)
		return NUMMATRIX(count_m, self.labels)

	def print_val(self,num):
		for i in range (0, len( (self.labels)[0] ) ):
			for j in range (0, len( (self.labels)[1] ) ):
				print  (self.labels)[0][i] + "::" + (self.labels)[1][j]
				gqltools.print_file( (self.val)[i][j].val, num)

#}}}

#{{{ class BEDL(EnvElement):
class BEDL(EnvElement):
	name = 'BEDL'
	def __init__(self,val,labels):
		# list of bedx 
		self.val = val
		# names of bedx
		self.labels = labels
	def count(self):
		count_r = [ NUM(gqltools.file_len(x.val)) for x in self.val]
		return NUMLIST(count_r, self.labels)

	def print_val(self, num):
		for i in range (0, len( self.labels ) ):
			print self.labels[i] 
			gqltools.print_file(self.val[i].val, num)

#}}}

#{{{ class NUM(EnvElement):
class NUM(EnvElement):
	name = 'NUM'
	def __init__(self,val):
		# list of bedx 
		self.val = np.float(val)
	def __str__(self):
		return str(self.val)
	def print_val(self,num):
		print str(self.val)

#}}}

#{{{  class NUMLIST(EvnElement):
class NUMLIST(EnvElement):
	name = 'NUMLIST'
	def __init__(self,val,labels):
		# list of bedx 
		self.val = np.array(val)
		self.labels = labels
	def print_val(self,num):
		print self
	def __str__(self):
		tmp_val = self.val.tolist()

		output = ''
		if len(self.labels) > 0:
			output = '\t'.join(self.labels) + '\n'
		output = output + '\t'.join( [str(x) for x in tmp_val] ) + '\n'
		return output
#}}}

#{{{ class NUMMATRIX(EnvElement):
class NUMMATRIX(EnvElement):
	name = 'NUMMATRIX'
	def __init__(self,val,labels):
		# list of bedx 
		self.val = np.matrix(val)
		self.labels = labels

	def print_val(self,num):
		print self

	def __str__(self):
		output = ''

		tmp_val = self.val.tolist()

		if len(self.labels) > 0:
			output = '\t' + '\t'.join(self.labels[1]) + '\n'

		for i in range (0, len(tmp_val)):
			if len(self.labels) > 0:
				output = output +  self.labels[0][i] + '\t' 
			output = output +  \
					'\t'.join( [str(x) for x in tmp_val[i] ] ) + '\n'
		return output

	def plot(self,filename):
		p = plt.imshow(self.val, interpolation='nearest', cmap='Blues')
		plt.colorbar(p)
		plt.savefig(filename)
		plt.close()
#}}}

#{{{  class LIST(EvnElement):
class LIST(EnvElement):
	name = 'LIST'
	def __init__(self,val,labels):
		# list of bedx 
		self.val = val
		self.labels = labels
	def print_val(self,num):
		print self
	def __str__(self):
		output = ''
		if len(self.labels) > 0:
			output = '\t'.join(self.labels) + '\n'
		output = output + '\t'.join( [str(x) for x in self.val] ) + '\n'
		return output
#}}}

bed_types = [BED3, BED4, BED6, BED12, BEDL]
saveable_types = [BED3, BED4, BED6, BED12, BEDN]
flat_bed_types = [BED3, BED4, BED6, BED12]
source_types = [BED3, BED4, BED6, BED12, GENOME]
printable_types = [BED3, BED4, BED6, BED12, BEDN, BEDM, BEDL, \
				   NUM, NUMLIST, NUMMATRIX, GENOME]
countable_types = [BED3, BED4, BED6, BED12, BEDN, BEDM, BEDL]
complementable_types = [BED3, BED4, BED6, BED12]
hilbertable_types = [BED3, BED4, BED6, BED12]
plotable_types = [NUMMATRIX]
sortable_types = [BED3, BED4, BED6, BED12]

source_type_map = {
	'LIST'	: LIST,
	'NUMMATRIX'	: NUMMATRIX,
	'NUMLIST'	: NUMLIST,
	'NUM'		: NUM,
	'BED3'		: BED3, 
	'BED4'		: BED4, 
	'BED6'		: BED6,
	'BED12'		: BED12, 
	'GENOME'	: GENOME
}
