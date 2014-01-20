
--- create foreign table corresponding to VCF files in a given directory(file) 

CREATE OR REPLACE FUNCTION proc_vcf_gtwide_create(table_name text, directory varchar)
  RETURNS integer AS
$BODY$
DECLARE
   sample_table TEXT;
   sample_str TEXT;
   tbl_sql TEXT;
BEGIN
  SELECT 'vcf_samples_' || pg_backend_pid()::text INTO  sample_table;
  
  EXECUTE 'CREATE FOREIGN TABLE IF NOT EXISTS ' ||  sample_table || '(
    sample VARCHAR,
    file VARCHAR,
    directory VARCHAR
  ) SERVER multicorn_vcf_sample' ;
 
  EXECUTE 'SELECT string_agg(quote_ident(v.sample::varchar(30)) || '' text,'', '''') FROM ' || sample_table || ' v WHERE directory = ''' || directory || ''''
     into  sample_str;

  EXECUTE 'DROP FOREIGN TABLE ' || sample_table;

  RAISE NOTICE 'Done obtaining samples using  %', sample_table;

  tbl_sql = 'CREATE FOREIGN TABLE ' || table_name || ' ( ' 
            || 'chrom VARCHAR, begin INT, stop INT,'
            || 'sample TEXT,'
            || 'pos INT,'
            || 'id VARCHAR, ref VARCHAR, alt VARCHAR,'
            || 'qual VARCHAR, filter VARCHAR,'
            || 'format VARCHAR, info VARCHAR,'
            || sample_str || 'file VARCHAR) '
            || 'SERVER multicorn_vcf_gt_wide '
            || 'OPTIONS( directory ''' || directory || ''')';

  -- RAISE NOTICE '%', tbl_sql;
  EXECUTE tbl_sql;

  RETURN 1;
END;
$BODY$
  LANGUAGE plpgsql;
  

