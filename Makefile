# Makefile
SHELL = /bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
DOCKER_IMAGE:=mathijsvdv/made-with-ml
CLUSTER_FILE:=cluster.yaml
RUNTIME_ENV_FILE:=runtime_env.yaml
JUPYTER_PORT:=6006
MLFLOW_PORT:=8080
RAY_ADDRESS:="http://127.0.0.1:8265/"

.PHONY: docker
docker:
	docker login
	docker build -t $(DOCKER_IMAGE) .
	docker push $(DOCKER_IMAGE)
	docker rmi $(DOCKER_IMAGE)

# Styling
.PHONY: style
style:
	pre-commit run black --all-files
	pre-commit run flake8 --all-files
	pre-commit run isort --all-files
	pre-commit run pyupgrade --all-files

# Clear cache and other generated files
.PHONY: clear_cache
clear_cache:
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -rf .coverage*

# Cleaning
.PHONY: clean
clean: style clear_cache

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

.PHONY: mlflow_server
mlflow_server:
	ray exec $(CLUSTER_FILE) 'mlflow server -h 0.0.0.0 -p $(MLFLOW_PORT) --backend-store-uri /tmp/mlflow/' --port-forward $(MLFLOW_PORT)

.PHONY: dashboard
dashboard:
	ray dashboard $(CLUSTER_FILE)

.PHONY: train
train:
	ray job submit --address $(RAY_ADDRESS) --runtime-env $(RUNTIME_ENV_FILE) -- python scripts/train.py
