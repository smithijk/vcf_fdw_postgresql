
\o /tmp/pg_vcf_wrapper/test_vcf_fdw.out

BEGIN;

CREATE EXTENSION IF NOT EXISTS multicorn;

CREATE SCHEMA IF NOT EXISTS vcffdw_test;

SET search_path TO vcffdw_test;

-- Create all servers

CREATE SERVER test_multicorn_vcf_sample FOREIGN DATA WRAPPER multicorn 
OPTIONS (wrapper 'multicorn.vcffdw.sampleFdw');

CREATE SERVER test_multicorn_vcf_info FOREIGN DATA WRAPPER multicorn 
OPTIONS (wrapper 'multicorn.vcffdw.infoFdw');

CREATE SERVER test_multicorn_vcf_genotype FOREIGN DATA WRAPPER multicorn 
OPTIONS (wrapper 'multicorn.vcffdw.genotypeFdw');

CREATE SERVER test_multicorn_vcf_gt_wide FOREIGN DATA WRAPPER multicorn 
OPTIONS (wrapper 'multicorn.vcffdw.gtWideFdw');

\i sql/utils.sql

-- Example for querying samples included in vcf files

CREATE FOREIGN TABLE IF NOT EXISTS test_vcf_sample_info(
  sample VARCHAR,
  file VARCHAR,
  directory VARCHAR
) SERVER test_multicorn_vcf_sample;


SELECT * FROM test_vcf_sample_info
WHERE directory = '/tmp/pg_vcf_wrapper/data/individual_files/*.gz';

select * from test_vcf_sample_info
where directory = '/tmp/pg_vcf_wrapper/data/aggregated_files/subset.chr8.1000.genomes.recode.vcf.gz';

-- Example for querying vcf info only without genotypes

CREATE FOREIGN TABLE IF NOT EXISTS test_vcf_snp_info(
  begin INT,
  stop INT,
  sample VARCHAR,
  chrom VARCHAR,
  pos INT,
  id VARCHAR,
  ref VARCHAR,
  alt VARCHAR,
  qual VARCHAR,
  filter VARCHAR,
  format VARCHAR,
  info VARCHAR,
  file VARCHAR,
  directory VARCHAR
) SERVER test_multicorn_vcf_info;


SELECT distinct chrom, pos, ref, alt, info FROM test_vcf_snp_info 
WHERE chrom = '8' AND begin = '100000' AND stop = '175000' 
AND directory = '/tmp/pg_vcf_wrapper/data/individual_files/*.vcf.gz';

DROP FOREIGN TABLE test_vcf_snp_info;

-- Example for querying vcf genotypes in long form

CREATE FOREIGN TABLE test_vcf_gt_long(
  begin INT,
  stop INT,
  sample VARCHAR,
  chrom VARCHAR,
  pos INT,
  id VARCHAR,
  ref VARCHAR,
  alt VARCHAR,
  qual VARCHAR,
  filter VARCHAR,
  format VARCHAR,
  info VARCHAR,
  genotype VARCHAR,
  file VARCHAR,
  directory VARCHAR
) SERVER test_multicorn_vcf_genotype;


select count(*) from test_vcf_gt_long
where chrom = '8' AND begin = '100000' AND stop = '175000'
and directory='/tmp/pg_vcf_wrapper/data/individual_files/*.vcf.gz';

select * from test_vcf_gt_long
where chrom = '8' AND begin = '100000' AND stop = '175000'
and directory='/tmp/pg_vcf_wrapper/data/individual_files/*.vcf.gz'
ORDER by pos, sample LIMIT 10;

SELECT count(*) FROM test_vcf_gt_long
WHERE chrom = '8' AND begin = '100000' AND stop = '175000' 
  AND sample in ('NA19332', 'NA19764')
  AND directory = '/tmp/pg_vcf_wrapper/data/individual_files/*.vcf.gz';

SELECT * FROM test_vcf_gt_long
WHERE chrom = '8' AND begin = '100000' AND stop = '175000' 
  AND sample in ('NA19332', 'NA19764')
  AND directory = '/tmp/pg_vcf_wrapper/data/individual_files/*.vcf.gz'
ORDER by pos, sample LIMIT 10;

DROP FOREIGN TABLE test_vcf_gt_long;

-- Example for querying vcf genotypes in wide form

select proc_vcf_gtwide_create('test_vcf_gt_wide', '/tmp/pg_vcf_wrapper/data/aggregated_files/*.vcf.gz');

select * from test_vcf_gt_wide
where chrom = '8' AND begin = '100000' AND stop = '175000'
ORDER BY pos LIMIT 10;

select chrom, pos, ref, alt, "NA19764", "NA19332" 
from test_vcf_gt_wide
where chrom = '8' AND begin = '100000' AND stop = '175000'
order by pos limit 10;

select * from test_vcf_gt_wide as v 
where chrom='8' and begin='100000' and stop='175000'
and sample = 'NA20126|NA18611|NA18637|NA12889'
order by pos limit 10;

-- Below query doesn't work
/*** 
select * from test_vcf_gt_wide as v 
where chrom='8' and begin='100000' and stop='175000'
and sample in ('NA20126', 'NA18611', 'NA18637', 'NA12889')
order by pos limit 10; 
***/

DROP FOREIGN TABLE test_vcf_gt_wide;

DROP SCHEMA vcffdw_test CASCADE;

DROP SERVER test_multicorn_vcf_sample;
DROP SERVER test_multicorn_vcf_info;
DROP SERVER test_multicorn_vcf_genotype;
DROP SERVER test_multicorn_vcf_gt_wide;

ROLLBACK;
