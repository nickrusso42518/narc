.DEFAULT_GOAL := test

.PHONY: test
test: clean lint unit dry

.PHONY: lint
lint:
	@echo "Starting  lint"
	find . -name "*.yaml" | xargs yamllint -s
	find . -name "*.py" | xargs pylint
	find . -name "*.py" | xargs black -l 85 --check
	@echo "Completed lint"

.PHONY: unit
unit:
	@echo "Starting  unit tests"
	pytest --verbose test_unit.py
	@echo "Completed unit tests"

.PHONY: dry
dry:
	@echo "Starting  dryruns"
	python runbook.py -d
	python runbook.py -d -f -s terse
	python runbook.py -d -f -s csv
	python runbook.py --dryrun --failonly --style json
	@echo "Completed dryruns"

.PHONY: clean
clean:
	@echo "Starting  clean"
	find . -name "*.pyc" | xargs -r rm
	rm -f nornir.log
	@echo "Starting  clean"
