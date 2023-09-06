# Makefile
SHELL = /bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
CLUSTER_FILE:=cluster.yaml
JUPYTER_PORT:=6006

# Styling
.PHONY: style
style:
	black .
	flake8
	python3 -m isort .
	pyupgrade

# Cleaning
.PHONY: clean
clean: style
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -rf .coverage*

.PHONY: rsync_up
rsync_up:
	ray rsync_up $(CLUSTER_FILE) '$(ROOT_DIR)/' '/home/ray/projects/Made-With-ML'

.PHONY: rsync_down
rsync_down:
	ray rsync_down $(CLUSTER_FILE) '/home/ray/projects/Made-With-ML/' '$(ROOT_DIR)'

.PHONY: attach
attach:
	ray attach $(CLUSTER_FILE)

.PHONY: jupyter_lab
jupyter_lab:
	ray exec $(CLUSTER_FILE) 'jupyter lab --port $(JUPYTER_PORT)' --port-forward $(JUPYTER_PORT)
