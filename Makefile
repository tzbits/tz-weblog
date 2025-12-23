PYLINT = pylint
YAPF = yapf
PYTHON = python3
PIP = pip

# The version should match your pyproject.toml
VERSION = 0.0.1

.PHONY: lint fix test presubmit dist distclean install uninstall reinstall

lint:
	find ./ -name \*.py \! -path "./build/*" | xargs $(PYLINT)

fix:
	find ./ -name \*.py \! -path "./build/*" | xargs $(YAPF) -i

test:
	cd tests && $(MAKE)

presubmit: fix lint test

dist:
	$(PYTHON) -m pip install --quiet build
	$(PYTHON) -m build

distclean:
	rm -Rf build
	rm -Rf dist
	rm -Rf *.egg-info

install: dist
	$(PIP) install dist/tz-weblog-$(VERSION)-py3-none-any.whl

# Use this for active coding; it links the source code so
# changes are reflected immediately without a reinstall.
dev-install:
	$(PIP) install -e .

uninstall:
	$(PIP) uninstall -y tz-weblog
