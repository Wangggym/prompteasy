SHELL := /bin/bash
HIDE ?= @

.PHONY: build

gen:
	-$(HIDE)rm -rf .venv
	$(HIDE)uv venv .venv --python=3.10.15
	$(HIDE)source .venv/bin/activate && uv sync

fix:
	$(HIDE)ruff format
	$(HIDE)ruff check --fix

dev:
	$(HIDE)uv run main.py

# Run a specific test case
run-case:
	$(HIDE)uv run main.py --case $(case) --repeat $(repeat)

# Run all test cases
run-all:
	$(HIDE)uv run main.py



