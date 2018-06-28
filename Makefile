# Note: "make test" won't halt if linting and coverage fail.

# Note: .egg and .egg-info folders aren't removed on "clean"
#       This is so that many make commands don't download
#       dependencies over and over again.

# Note: All these tasks are simply _recommendations_ meant to
# 		make your life easier. Change what you will but please
#		*keep the names of the tasks the same*!

# anandni
# Mon Jun 13 16:00:12 CDT 2016


.PHONY: help
help:
	@echo ""
	@echo " help"
	@echo "     Display this message"
	@echo " all"
	@echo "     Clean build artifacts, run tests, build wheel & documentation"
	@echo " build"
	@echo "     Run tests and build a wheel"
	@echo " bump"
	@echo "     Increment patch number and push tags to remote"
	@echo " clean"
	@echo "     Remove all build artifacts"
	@echo " coverage"
	@echo "     Run and display coverage report"
	@echo " dev_install"
	@echo "     Install editable version of package into virtualenv"
	@echo " doc"
	@echo "     Build HTML documentation"
	@echo " doc_serve"
	@echo "     Serve documentation on localhost:8888 and watch source for changes"
	@echo " doc_publish"
	@echo "     Build and publish HTML documentation to pypidocs.phibred.com"
	@echo " install"
	@echo "     Install package into virtualenv"
	@echo " lint"
	@echo "     Run linter and display report"
	@echo " publish"
	@echo "     Run tests, make wheel, push to our local PyPI repository"
	@echo " sdist"
	@echo "     Build source distribution"
	@echo " test"
	@echo "     Run linter, coverage reporter, and all tests"
	@echo " test_publish"
	@echo "     Publish package to the local, test PyPI repository"
	@echo ""
	@echo " > To bootstrap dependencies, run 'make dev_install'"
	@echo ""


.PHONY: check_venv
check_venv:

ifndef VIRTUAL_ENV
	$(error "! You don't appear to be in a virtual environment.")
endif


.PHONY: all
all: check_venv clean test build doc


.PHONY: build
build: check_venv test
	python setup.py sdist
	python setup.py bdist_wheel
	python setup.py bdist_egg


.PHONY: bump
bump:
ifneq ($(shell bash -c 'bumpversion' >/dev/null 2>&1; echo $$?), 1)
	$(warning "! Could not find bumpversion; attempting install")
	pip install bumpversion
endif
	bumpversion patch
	git push --follow-tags


.PHONY: clean
clean: check_venv
	rm -rf dist build .cache*
	rm -rf docs/build
	find . -type f -iname "*.pyc" | xargs rm -rf {}
	find . -type d -iname "__pycache__" | xargs rm -rf {}


.PHONY: coverage
coverage: check_venv
	-python setup.py -q test --addopts --cov=sbs


.PHONY: dev_install
dev_install: check_venv
	pip install -e .


.PHONY: doc
doc: check_venv
ifneq ($(shell bash -c 'sphinx-build' >/dev/null 2>&1; echo $$?), 1)
	$(warning "! Could not find Sphinx; attempting install")
	pip install sphinx sphinx_rtd_theme
endif
	cd docs && make clean && make html


.PHONY: doc_serve
doc_serve: doc
ifneq ($(shell bash -c 'livereload --version' >/dev/null 2>&1; echo $$?), 2)
	$(warning "! Could not find live-reloader; attempting install")
	pip install livereload
endif
	python -c "from livereload import Server, shell; server = Server(); server.watch('docs/source/*.rst', shell('make html',   cwd='docs')); server.serve(port=8888, host='localhost', root='docs/build/html')"


.PHONY: doc_publish
doc_publish: doc
	# I used this initially
	# sed -n 's/.*\([0-9]\+\.[0-9]\+\.[0-9]\+\).*/\1/p'
	# However, the regex I'm using below seems better since it will
	# (a) look only at __version__
	# (b) not require the user to employ semantic versioning

	$(eval PROJECT_VERSION=$(shell cat sbs/__init__.py | sed -rn "s/.*__version__[ ]*=[ ]*'(.*)'/\1/p"))
	cd docs/build && \
	tar -czvf sbs.docs-v$(PROJECT_VERSION).tgz html/ && \
	curl -X POST -H "Cache-Control: no-cache" -H "Content-Type: multipart/form-data" -F "docball=@sbs.docs-v$(PROJECT_VERSION).tgz" "http://pypidocs.phibred.com/publish";


.PHONY: install
install: check_venv
	pip install .


.PHONY: lint
lint: check_venv
	-python setup.py -q test --addopts --flake8


.PHONY: publish
publish: check_venv test build
	python setup.py sdist upload -r pypi-local
	python setup.py bdist_wheel upload -r pypi-local


.PHONY: sdist
sdist: check_venv
	python setup.py sdist


.PHONY: test
test: check_venv clean lint coverage
	python setup.py -q test


.PHONY: test_publish
test_publish: check_venv test build
	python setup.py sdist upload -r pypi-local-test
	python setup.py bdist_wheel upload -r pypi-local-test
