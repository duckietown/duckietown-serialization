all:


bump-upload:
	$(MAKE) bump
	$(MAKE) upload

bump: # v2
	bumpversion patch
	git push --tags
	git push
upload: # v3
	dts build_utils check-not-dirty
	dts build_utils check-tagged
	dt-check-need-upload --package duckietown-serialization-ds1 make upload-do

upload-do:
	rm -f dist/*
	rm -rf src/*.egg-info
	python3 setup.py sdist
	twine upload --skip-existing --verbose dist/*



tests-clean:
	rm -rf out-comptests

tests:
	comptests --nonose duckietown_serialization_tests


branch=$(shell git rev-parse --abbrev-ref HEAD)
#
#tag_rpi=duckietown/rpi-duckietown-shell:$(branch)
#tag_x86=duckietown/duckietown-shell:$(branch)
#
#build: build-rpi build-x86
#
#push: push-rpi push-x86
#
#build-rpi:
#	docker build -t $(tag_rpi) -f Dockerfile.rpi .
#
#build-x86:
#	docker build -t $(tag_x86) -f Dockerfile .
#
#build-x86-no-cache:
#	docker build -t $(tag_x86) -f Dockerfile --no-cache .
#
#push-rpi:
#	docker push $(tag_rpi)
#
#push-x86:
#	docker push $(tag_x86)
#
#test:
#	make -C testing



name=dt-ser-python3

test-python3:
	docker stop $(name) || true
	docker rm $(name) || true

	docker run -it -v "$(shell realpath $(PWD)):/dt-ser" -w /dt-ser --name $(name) python:3 /bin/bash

test-python3-install:
	pip install -r requirements.txt
	pip install nose
	python setup.py develop --no-deps
