
PYTHON=/usr/bin/python
MANAGE=$(PYTHON) app/manage.py

default: help
    
dev:
    @export TEAGARDEN_DEBUG=1; cd app; $(MANAGE) runserver

help:
    @echo "Available commands:"
    @sed -n '/^[a-zA-Z0-9_.]*:/s/:.*//p' <Makefile | sort

fixture:
    @$(MANAGE) dumpdata teagarden --indent=2 > app/teagarden/fixtures/initial_data.yaml

docs/datamodel.png:
    @$(MANAGE) graph_models -a -g -o $@

js-compiled:
    @$(PYTHON) closure/closure/bin/calcdeps.py -i app/teagarden/static/js/script.js -p closure -o compiled -c compiler.jar > app/teagarden/static/js/script.js.compiled

js-compiled-optimized:
    @$(PYTHON) closure/closure/bin/calcdeps.py -i app/teagarden/static/js/script.js -p closure -o compiled -c compiler.jar -f "--compilation_level=ADVANCED_OPTIMIZATIONS" > app/teagarden/static/js/script.js.compiled

po:
    @$(MANAGE) makemessages -a

mo:
    @$(MANAGE) compilemessages
