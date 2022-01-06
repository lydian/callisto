.PHONY: venv start-dev
venv:
	tox -e venv --notest

build-js:
	cd front && npm run build

start-dev: venv
	venv/bin/python cli.py start-dev --port 5001

test:
	tox
