PYTHON=python
MANAGE=$(PYTHON) app/manage.py


default: help

dev:
	@export TEAGARDEN_DEBUG=1; $(MANAGE) runserver

help:
	@echo "Available commands:"
	@sed -n '/^[a-zA-Z0-9_.]*:/s/:.*//p' <Makefile | sort

js-compiled:
	@$(PYTHON) closure/closure/bin/calcdeps.py -i app/teagarden/static/js/script.js -p closure -o compiled -c compiler.jar > app/teagarden/static/js/script.js.compiled

js-po:
	@cd app/teagarden; $(PYTHON) ../manage.py makemessages --domain=djangojs -a

po:
	@cd app/teagarden; $(PYTHON) ../manage.py makemessages -a

prod:
	@$(MANAGE) runfcgi --settings=settings daemonize=false host=127.0.0.1 port=8083

mo:
	@cd app/teagarden; $(PYTHON) ../manage.py compilemessages

sprites:
	@rm -f data/sprites/sprites.zip
	@zip -j -v data/sprites/sprites.zip data/sprites/*.png
