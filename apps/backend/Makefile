# https://gist.github.com/prwhite/8168133

.PHONY: help test install-requirements

help:                                 ## show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

test:                                 ## run tests
	cd tests && pytest

install-requirements:                 ## install requirements
	pip3 install -r requirements.txt

run:                                 ## run tests
	cd src/green-shifting && python3 main.py
