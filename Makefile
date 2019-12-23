.DEFAULT_GOAL := test

.PHONY: test
test: clean lint dry

.PHONY: lint
lint:
	@echo "Starting  lint"
	find . -name "*.yaml" | xargs yamllint -s
	find . -name "*.py" | xargs pylint
	find . -name "*.py" | xargs black -l 85 --check
	@echo "Completed lint"

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
	rm -rf __pycache__
	rm -f nornir.log
	@echo "Starting  clean"
