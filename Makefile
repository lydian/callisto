.PHONY: venv start-dev test build build-js
venv:
	tox -e venv --notest

start-dev: venv
	venv/bin/python cli.py start-dev --port 5001


front/node_modules/:
	cd front && npm install

build-js: front/node_modules/
	cd front && npm run build


test: build-js
	tox


build: build-js
	python setup.py sdist
	python setup.py bdist_wheel
