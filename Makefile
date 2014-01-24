
MULTICORN = /pub/share/vcf_proj/multicorn-1.0.0.beta
TESTDIR = /tmp/pg_vcf_wrapper
TESTOUTPUT = ${TESTDIR}/test_vcf_fdw.out

install : python/multicorn/vcffdw.py
	cp python/multicorn/vcffdw.py ${MULTICORN}/python/multicorn/
	cd ${MULTICORN} && python setup.py install

.PHONY: test

testdata : 
	mkdir -p ${TESTDIR}/data/  
	cp -r test/data/* ${TESTDIR}/data/

test : testdata
	@while [ -z "$$PGTEST" ]; do \
        read -r -p "Database used for testing: " PGTEST;\
    done && \
	psql $${PGTEST} < test/test_vcf_fdw.sql > ${TESTOUTPUT} 
	@diff ${TESTOUTPUT} ${TESTDIR}/data/expected.out && echo "test PASSED" || echo "test FAILED"
	@echo SQL output is saved at  ${TESTOUTPUT}.

clean:
	rm -rf ${TESTDIR}
