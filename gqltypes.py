import re

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

	def __init__(self,val,tmp):
		self.val = val;
		self.tmp = tmp;

	def __str__(self):
		return "(" + self.val + "," + str(self.tmp) + ")"
#}}}

#{{{class BED3(EnvElement,SourceFile):
class BED3(EnvElement,SourceFile):
	name = 'BED3'
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

#{{{ class BED6(EnvElement,SourceFile):
class BED6(EnvElement,SourceFile):
	name = 'BED6'
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

#}}}

#{{{ class BEDM(EnvElement):
class BEDM(EnvElement):
	name = 'BEDM'
	def __init__(self,val,labels):
		self.val = val
		self.labels = labels
#}}}

#{{{ class BEDL(EnvElement):
class BEDL(EnvElement):
	name = 'BEDL'
	def __init__(self,val,labels):
		# list of bedx 
		self.val = val
		# names of bedx
		self.labels = labels
#}}}

source_types = (BED3, BED6, BED12, GENOME)
source_type_map = {
	'BED3' : BED3, 
	'BED6' : BED6,
	'BED12' : BED12, 
	'GENOME' : GENOME
}
