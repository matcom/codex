.PHONY: source docs publish tests

docs: source
	(cd docs && quarto render)

dev:
	find docs | grep md$ | entr make source

source:
	@illiterate -d . docs/*.md
	@make tests

publish: source
	(cd docs && quarto publish gh-pages)

tests:
	@PYTHONPATH=src pytest
