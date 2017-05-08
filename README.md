

A PostgreSQL foreign data wrapper for VCF files.

This is a PostgreSQL foreign data wrapper to one or a collection of VCF files. The CyVCF package is used to parse the VCF files while the Multicorn library is used to render the results into a PostgreSQL table.

Requirements
============

1. PostgreSQL 9.4 or greater
2. Multicorn 1.0.2 or greater 
3. modified CyVCF library that accepts user input as to which samples to retrieve. See https://github.com/wenjiany/cyvcf
4. VCF files which are tabix indexed


Installation
============

1. Copy ./python/multicorn/vcffdw.py to multicorn-version/python/multicorn/ directory.
2. cd multicorn-version
3. make & make install 
4. Execute the following SQL commands in PostgreSQL:

```sql
CREATE EXTENSION multicorn;

CREATE SERVER multicorn_vcf_genotype FOREIGN DATA WRAPPER multicorn 
OPTIONS (wrapper 'multicorn.vcffdw.genotypeFdw');

CREATE FOREIGN TABLE vcfinfo(
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
) SERVER multicorn_vcf_genotype;

CREATE SERVER multicorn_vcf_info FOREIGN DATA WRAPPER multicorn 
OPTIONS (wrapper 'multicorn.vcffdw.infoFdw');

CREATE FOREIGN TABLE vcf_snp_info(
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
) SERVER multicorn_vcf_info;

CREATE SERVER multicorn_vcf_info FOREIGN DATA WRAPPER multicorn
OPTIONS (wrapper 'multicorn.vcffdw.sampleFdw');

CREATE FOREIGN TABLE vcf_sample_info(
  sample VARCHAR,
  file VARCHAR,
  directory VARCHAR
) SERVER multicorn_vcf_sample;
```

Basic Usage
============

The query below retrieves info and genotypes for all samples in the vcf files for the SNPs within the specified region.

```sql
SELECT * FROM vcfinfo WHERE chrom = '8' AND begin = '100000' AND stop = '175000' 
AND directory = '/path/to/vcf/files/*gz';
```

The query below retrieves info and genotypes only for samples "sample1" and "sample2"

```sql
SELECT * FROM vcfinfo WHERE chrom = '8' AND begin = '100000' AND stop = '175000' 
  AND sample in ('sample1', 'sample2') AND directory = '/path/to/vcf/files/*gz';
```

The query below retrieves sampleids included in the vcf files.

```sql

SELECT * from vcf_sample_info WHERE 
      directory = '/path/to/vcf/file.vcf.gz';
```

The query below retrieves variant information included in the vcf files, but
does not retrieve genotypes.

```sql

SELECT distinct chrom, pos, ref, alt, info FROM vcf_snp_info 
WHERE chrom = '8' AND begin = '100000' AND stop = '175000' 
AND directory = '/path/to/vcf_files/*gz';
```

The query below uses a crosstab to retrieve sample genotypes in wide form.

```sql
SELECT * FROM CROSSTAB(
'SELECT pos, chrom, id, sample, genotype FROM vcfinfo 
WHERE chrom = ''8'' AND begin = ''100000'' AND stop = ''175000'' AND directory = ''/path/to/vcf_files/*gz'' order by 1', 
'SELECT sample from vcf_sample_info WHERE directory = ''/path/to/vcf_files/*gz'' and sample in (''HG00096'', ''HG00126'') ')
AS (pos INT, chrom TEXT, id TEXT, "HG00096" TEXT, "HG00126" TEXT)
```

The query below does the same as above but much more quickly via an intermediate table.

```sql
SELECT proc_vcf_gtwide_create('test_vcf_gt_wide', '/path/to/vcf_files/*.vcf.gz');

SELECT * FROM test_vcf_gt_wide 
WHERE chrom='8' AND begin='100000' AND stop='175000'
AND sample = 'NA20126|NA18611|NA18637|NA12889'
ORDER BY pos limit 10;
```
Notes:

* You are able to join these foreign data tables with ordinary data tables. The test scripts included here test this capability.


Disclaimer
==========

This software comes without any warranty whatsoever.  Use at your own risk.
