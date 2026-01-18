.PHONY: source docs publish tests

source:
	@illiterate -d . docs/*.md
	@make tests

dev:
	find docs | grep md$ | entr make source

docs: source
	(cd docs && quarto render)

publish:
	(cd docs && quarto publish gh-pages)

tests:
	pytest
