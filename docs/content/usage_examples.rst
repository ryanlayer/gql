##############
Usage examples
##############


-------------------------------------------------
1. Predict lincRNA genes involved in differentiation
-------------------------------------------------

.............
Overview
.............
What are we trying to do, how are we tackling the problem?
What experiments and what are the relevant datasets?


.............
GQL commands
.............

1. First, we must load the existing mouse annotations for exons and microRNAs ::
	
	mm9_exons = LOAD "data/mm9_exons.bed";
	mm9_miRNA = LOAD "data/mm9_miRNA.id.bed";


2. For TSS sites, we want to load the track and recast it as a BED3 file::

	mm9_5KB_tss_o = LOAD "data/mm9_tss_strand_5KB.name.bed";
	mm9_5KB_tss = CAST mm9_5KB_tss_o AS BED3;

3. Now, we want to load the experimental datasets::

	MB_rnaseq = LOAD "data/MB_rnaseq.bed";
	MB_polii = LOAD "data/PolII_MB-Sonicated_input_MB.bed";
	

4. To do::

	MB_pollii_rnaseq = MERGEMIN MB_rnaseq, MB_polii WHERE SCORE(COUNT);
	MB_sites = FILTER MB_pollii_rnaseq WHERE SCORE(==2);

5. To do::

	MT_rnaseq = LOAD "data/MT_rnaseq.bed";
	MT_polii = LOAD "data/PolII_MT-Sonicated_input_MT.bed";
	MT_pollii_rnaseq = MERGEMIN MT_rnaseq, MT_polii WHERE SCORE(COUNT);
	MT_sites = FILTER MT_pollii_rnaseq WHERE SCORE(==2);

6. To do::

	MB_only = MB_sites SUBTRACT MT_sites,mm9_exons,mm9_miRNA,mm9_5KB_tss;
	MT_only = MT_sites SUBTRACT MB_sites,mm9_exons,mm9_miRNA,mm9_5KB_tss;

7. Save the results and design assays to test these lincRNAs::
	
	SAVE MB_only AS "MB_only.bed";
	SAVE MT_only AS "MT_only.bed";