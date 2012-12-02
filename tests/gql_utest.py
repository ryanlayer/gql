#!/usr/bin/env python
import random
import unittest
import sys
sys.path.append('../')
import gqltools
import gqltypes
import pybedtools
import os.path
import os
import json

class testGQL(unittest.TestCase):

	#{{{ def setUp(self):
	def setUp(self):
		json_data=open('../gql.conf')
		gqltools.config = json.load(json_data)
	#}}}

	#{{{ def test_tempfile_management(self):
	def test_tempfile_management(self):
		R_file_name = gqltools.get_temp_file_name(pybedtools.get_tempdir(), \
										 'unittest', \
										 'tmp')
		r = random.randint(1,sys.maxint)
		f = open(R_file_name, 'w')
		f.write(str(r))
		f.close()

		# test to see if the file was created
		self.assertTrue(os.path.isfile(R_file_name))

		R=gqltypes.BED6(R_file_name, True)

		gqltools.add_tmp_file(R)

		gqltools.clear_tmp_files()

		self.assertEqual(os.path.isfile(R_file_name), False)
	#}}}

	##{{{ def test_load_file(self):
	def test_load_file(self):
		a = gqltools.load_file('mm9:c2c12:chipseq','auto')
		gqltools.print_val(a,10)
		self.assertEqual(type(a), gqltypes.BEDL)

		a = gqltools.load_file('../data/a.bed','auto')
		self.assertEqual(type(a), gqltypes.BED6)

		a = gqltools.load_file('../data/bed3.bed','auto')
		self.assertEqual(type(a), gqltypes.BED3)

		a = gqltools.load_file('../data/bed12.bed','auto')
		self.assertEqual(type(a), gqltypes.BED12)

		a = gqltools.load_file('../data/a.bed','BED6')
		self.assertEqual(type(a), gqltypes.BED6)

		was_error = False
		try:
			a = gqltools.load_file('../data/a.bed','BED3')
		except Exception:
			was_error = True

		self.assertTrue(was_error)

		a = gqltools.load_file('../data/*.bed','auto')
		self.assertEqual(type(a), gqltypes.BEDL)

		a = gqltools.load_file('../data/bed12.bed','auto')
		c = gqltools.cast(a,gqltypes.BED6)
		self.assertEqual(type(c), gqltypes.BED6)

		f = open(c.val)
		num_cols = 0
		for line in f:
			cols = line.rstrip().split('\t')
			num_cols = len(cols)
		f.close()
		self.assertEqual(num_cols, 6)


		c = gqltools.cast(a,gqltypes.BED4)
		self.assertEqual(type(c), gqltypes.BED4)

		c = gqltools.cast(a,gqltypes.BED3)
		self.assertEqual(type(c), gqltypes.BED3)
	#}}}

	##{{{ def test_count(self):
	def test_count(self):
		a = gqltools.load_file('../data/a.bed','auto')
		C = gqltools.count(a)
		#gqltools.print_val(C,-1)

		b = gqltools.load_file('../data/tiny*.bed','auto')
		C = gqltools.count(b)
		#gqltools.print_val(C,-1)


		ordered_bed_list_N = [gqltools.load_file('../data/a.bed','auto')]
		ordered_bed_list_M = [gqltools.load_file('../data/b.bed','auto'), \
				gqltools.load_file('../data/d.bed','auto') ]

		label_list_N = ['a']
		label_list_M = ['b','d']

		R = gqltools.binary_intersect_beds(ordered_bed_list_N, \
						  label_list_N, \
						  ordered_bed_list_M, \
						  label_list_M)

		C = gqltools.count(R)
		#gqltools.print_val(C,-1)
		#print C

	#}}}

	#{{{ def test_binary_subtract(self):
	def test_binary_subtract(self):

		bed_N = gqltools.load_file('../data/a.bed','auto')
		ordered_bed_list_M = [gqltools.load_file('../data/b.bed','auto'), \
				gqltools.load_file('../data/d.bed','auto') ]

		R = gqltools.subtract_beds(bed_N, ordered_bed_list_M)

		self.assertEqual(R.__class__.__name__, bed_N.__class__.__name__)

		ordered_bed_list_M = [gqltools.load_file('../data/tiny*.bed','auto')]

		R = gqltools.subtract_beds(bed_N, ordered_bed_list_M)

		self.assertEqual(type(R), type(bed_N))

	#}}}

	#{{{ def test_uniary_intersect(self):
	def test_uniary_intersect(self):

		ordered_bed_list = [\
				gqltools.load_file('../data/a.bed','auto'), \
				gqltools.load_file('../data/b.bed','auto'), \
				gqltools.load_file('../data/d.bed','auto') ]

		bed_labels = ['a','b','c']

		R = gqltools.unary_intersect_beds(ordered_bed_list, bed_labels)
		self.assertEqual(type(R), gqltypes.BEDN)

		ordered_bed_list = [gqltools.load_file('../data/tiny*.bed','auto')]
		R = gqltools.unary_intersect_beds(ordered_bed_list, bed_labels)
		self.assertEqual(type(R), gqltypes.BEDN)


	#}}}

	#{{{ def test_binary_intersect(self):
	def test_binary_intersect(self):

		ordered_bed_list_N = [gqltools.load_file('../data/a.bed','auto')]
		ordered_bed_list_M = [gqltools.load_file('../data/b.bed','auto'), \
				gqltools.load_file('../data/d.bed','auto') ]

		label_list_N = ['a']
		label_list_M = ['b','d']

		R = gqltools.binary_intersect_beds(ordered_bed_list_N, \
						  label_list_N, \
						  ordered_bed_list_M, \
						  label_list_M)

		self.assertEqual(type(R), gqltypes.BEDM)
		self.assertEqual(len(R.labels[0]), 1)
		self.assertEqual(len(R.labels[1]), 2)
		self.assertEqual(len(R.val), 1)
		self.assertEqual(len(R.val[0]), 2)

		ordered_bed_list_N = [gqltools.load_file('../data/a.bed','auto')]
		ordered_bed_list_M = [gqltools.load_file('../data/tiny*.bed','auto')]

		label_list_N = ['a']
		label_list_M = ['d']

		R = gqltools.binary_intersect_beds(ordered_bed_list_N, \
						  label_list_N, \
						  ordered_bed_list_M, \
						  label_list_M)

		self.assertEqual(type(R), gqltypes.BEDM)
	#}}}

	#{{{ def test_jaccard_beds(self):
	def test_jaccard_beds(self):
		ordered_bed_list_N = [gqltools.load_file('../data/a.bed','auto')]
		ordered_bed_list_M = [gqltools.load_file('../data/b.bed','auto'), \
				gqltools.load_file('../data/d.bed','auto') ]

		label_list_N = ['a']
		label_list_M = ['b','d']

		R = gqltools.binary_jaccard_beds(ordered_bed_list_N, \
						  label_list_N, \
						  ordered_bed_list_M, \
						  label_list_M)

		self.assertEqual(type(R), gqltypes.NUMMATRIX)
		#gqltools.print_val(R,-1)
	#}}}

	#{{{ def test_merge(self):
	def test_merge(self):

		for merge_type in ('min','max','flat'):
			ordered_bed_list = [gqltools.load_file('../data/a.bed','auto'), \
						gqltools.load_file('../data/b.bed','auto'), \
						gqltools.load_file('../data/d.bed','auto') ]

			mods = {}

			R = gqltools.merge_beds(merge_type,ordered_bed_list, mods)

			self.assertEqual(type(R), gqltypes.BED3)

			was_error = False
			try:
				mods = {'distance':10}
				R = gqltools.merge_beds('flat',ordered_bed_list, mods)
			except Exception:
				was_error = True
			self.assertTrue(was_error)

			was_error = False
			try:
				mods = {'name':'OTHER'}
				R = gqltools.merge_beds('flat',ordered_bed_list, mods)
			except Exception:
				was_error = True
			self.assertTrue(was_error)

			for func in ['MIN', 'MAX', 'SUM', 'MEAN', 'MEDIAN', 'MODE', \
					'ANITMODE', 'COLLAPSE', 'COUNT']:
				mods = {'score':func}
				R = gqltools.merge_beds(merge_type,ordered_bed_list, mods)
				self.assertEqual(type(R), gqltypes.BED6)

			ordered_bed_list = [gqltools.load_file('../data/tiny*.bed','auto')]

			for func in ['MIN', 'MAX', 'SUM', 'MEAN', 'MEDIAN', 'MODE', \
					'ANITMODE', 'COLLAPSE', 'COUNT']:
				mods = {'score':func}
				R = gqltools.merge_beds(merge_type,ordered_bed_list, mods)
				self.assertEqual(type(R), gqltypes.BED6)

	#}}}

	#{{{ def tearDown(self):
	def tearDown(self):
		gqltools.clear_tmp_files()
	#}}}


if __name__ == '__main__':
	unittest.main()
