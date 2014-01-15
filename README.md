

A PostgreSQL foreign data wrapper for VCF files.

This is a PostgreSQL foreign data wrapper to one or a collection of VCF files. The CyVCF package is used to parse the VCF files while the Multicorn library is used to render the results into a PostgreSQL table.

Requirements
============

1. PostgreSQL 9.1 or greater
2. Multicorn 0.9.1 or greater
3. modified CyVCF library that accepts user input as to which samples to retrieve
4. VCF files are tabix indexed


Installation
============

1. Copy vcf_wrapper to multicorn-version/python/multicorn/ directory.
2. cd multicorn-version
3. make && make install 
4. Execute the following SQL commands in PostgreSQL:

```sql
CREATE SERVER multicorn_vcf FOREIGN DATA WRAPPER multicorn 
OPTIONS (wrapper 'multicorn.vcf_wrapper.vcfFdw');

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
) SERVER multicorn_vcf;
```


Basic Usage
============

Query below retrieves SNPs info and genotypes for all samples in the vcf files for the SNPs within the specified region.

```sql
SELECT * FROM vcfinfo WHERE chrom = 'chr8' AND begin = '38268656' AND stop = '38326352' 
AND directory = '/path/to/vcf/files/*gz';
```

Query below retrieves SNPs info and genotypes only for samples "sample1" and "sample2"

```sql
SELECT * FROM vcfinfo WHERE chrom = 'chr8' AND begin = '38268656' AND stop = '38326352' 
  AND sample in ('sample1', 'sample2') AND directory = '/path/to/vcf/files/*gz';
```

