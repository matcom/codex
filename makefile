.PHONY: source docs publish tests

dev:
	find docs | grep md$ | entr make source

source:
	@illiterate -d . docs/*.md
	@make tests

docs: source
	(cd docs && quarto render)

publish:
	(cd docs && quarto publish gh-pages)

tests:
	pytest
