.PHONY: lint
lint:
	@echo "Starting  lint"
	find . -name "*.yaml" | xargs yamllint -s
	find . -name "*.py" | xargs pylint
	find . -name "*.py" | xargs black -l 80 --check
	@echo "Completed lint"
