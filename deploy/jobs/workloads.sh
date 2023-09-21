#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$PWD
export RAY_AIR_REENABLE_DEPRECATED_SYNC_TO_HEAD_NODE=1
export S3_BUCKET=madewithml-mathissimo
mkdir results

# Test data
export RESULTS_FILE=results/test_data_results.txt
export DATASET_LOC="https://raw.githubusercontent.com/GokuMohandas/Made-With-ML/main/datasets/dataset.csv"
pytest --dataset-loc=$DATASET_LOC tests/data --verbose --disable-warnings > $RESULTS_FILE
cat $RESULTS_FILE

# Test code
export RESULTS_FILE=results/test_code_results.txt
python -m pytest tests/code --verbose --disable-warnings > $RESULTS_FILE
cat $RESULTS_FILE

# Train
export RESULTS_FILE=results/training_results.json
python scripts/train.py results_fp=$RESULTS_FILE

# Get and save run ID
export RUN_ID=$(python -c "import os; from madewithml import utils; d = utils.load_dict(os.getenv('RESULTS_FILE')); print(d['run_id'])")
export RUN_ID_FILE=results/run_id.txt
echo $RUN_ID > $RUN_ID_FILE  # used for serving later

# Evaluate
export RESULTS_FILE=results/evaluation_results.json
python scripts/evaluate.py run_id=$RUN_ID results_fp=$RESULTS_FILE

# Test model
RESULTS_FILE=results/test_model_results.txt
pytest --run-id=$RUN_ID tests/model --verbose --disable-warnings > $RESULTS_FILE
cat $RESULTS_FILE

# Save to S3
export MODEL_REGISTRY=$(python -c "from madewithml import config; print(config.MODEL_REGISTRY)")
aws s3 cp $MODEL_REGISTRY s3://$S3_BUCKET/mlflow/ --recursive
aws s3 cp results/ s3://$S3_BUCKET/results/ --recursive
