
MULTICORN = /pub/share/vcf_proj/multicorn-1.0.0.beta

install : python/multicorn/vcffdw.py
	cp python/multicorn/vcffdw.py ${MULTICORN}/python/multicorn/
	cd ${MULTICORN} && python setup.py install

.PHONY: test

testdata : 
	mkdir -p /tmp/pg_vcf_wrapper/data/  
	cp -r test/data/* /tmp/pg_vcf_wrapper/data/

test : testdata
	@while [ -z "$$PGTEST" ]; do \
        read -r -p "Database used for testing: " PGTEST;\
    done && \
	psql $${PGTEST} < test/test_vcf_fdw.sql
	@echo check /tmp/pg_vcf_wrapper/test_vcf_fdw.out for output.
	@diff /tmp/pg_vcf_wrapper/test_vcf_fdw.out /tmp/pg_vcf_wrapper/data/expected.out && echo "test PASSED" || echo "test FAILED"

clean:
	rm -rf /tmp/pg_vcf_wrapper
