import re

#chr_re = r'chr[0-9XYM]+$'
chr_re = r'chr.+$'
string_re = r'.*$'
float_re = r'-?[0-9]+(\.[0-9]*)?'
one_digit_re = r'[0-9]+$'
cs_digits_re = r'[0-9]+(,[0-9]+)*'
strand_re = r'\+|\-'
rgb_re = r'[0-9]+,[0-9]+,[0-9]+$'
	

# each entry represents a column
bed3 = [ chr_re, #chrom
		 one_digit_re, #start
		 one_digit_re, #end
]

bed6 = [ chr_re,		#chrom
		 one_digit_re,	#start
		 one_digit_re,	#end
		 string_re,		#name
		 float_re,		#score
		 strand_re,		#strand
]

bed12 = [ chr_re,		#chrom
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

genome = [	chr_re, #chrom
			one_digit_re, #length

]

filetypes = {
		'BED3'		: bed3,
		'BED6'		: bed6,
		'BED12'		: bed12,
		'GENOME'	: genome,
}
