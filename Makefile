
.PHONY: test-env test testdata install clean

TEST_DIR_PRE := /tmp/

install : python/multicorn/vcffdw.py
	@while [ -z "$$MULTICORN" ]; do \
	    read -r -p "Path to Multicorn Source: " MULTICORN; \
	done && \
	cp python/multicorn/vcffdw.py $${MULTICORN}/python/multicorn/ && \
	cd $${MULTICORN} && python setup.py install

test-env:
	$(eval TEST_DIR := $(shell while [ -z "$$VCF_TESTDIR" ]; do \
	    read -r -p "Relative path used for testing (${TEST_DIR_PRE}): " VCF_TESTDIR; \
	done && \
	echo $${VCF_TESTDIR}))
	$(eval TEST_DIR := ${TEST_DIR_PRE}/${TEST_DIR}/test_vcf_fdw.out)
	$(eval TESTOUTPUT := ${TEST_DIR}/test_vcf_fdw.out)

testdata : test-env 
	mkdir -p ${TEST_DIR}/data/  
	cp -r test/data/* ${TEST_DIR}/data/

test : testdata
	@while [ -z "$$PGTEST" ]; do \
	    read -r -p "Database used for testing: " PGTEST; \
	done && \
	while [ -z "$$PGUSER" ]; do \
	    read -r -p "Username for connecting to DB: " PGUSER; \
	done && \
	psql $${PGTEST} -U $${PGUSER} < test/test_vcf_fdw.sql > ${TESTOUTPUT} 
	@diff ${TESTOUTPUT} ${TEST_DIR}/data/expected.out && echo "test PASSED" || echo "test FAILED"
	@echo SQL output is saved at  ${TESTOUTPUT}.

clean: test-env 
	rm -rf ${TEST_DIR}
