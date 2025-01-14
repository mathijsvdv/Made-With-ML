import json
from typing import Any, Dict, Iterable, List
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import ray
import torch
from numpyencoder import NumpyEncoder
from ray.air import Result
from ray.train.torch import TorchPredictor
from ray.train.torch.torch_checkpoint import TorchCheckpoint

from madewithml.config import logger, mlflow


def decode(indices: Iterable[Any], index_to_class: Dict) -> List:
    """Decode indices to labels.

    Args:
        indices (Iterable[Any]): Iterable (list, array, etc.) with indices.
        index_to_class (Dict): mapping between indices and labels.

    Returns:
        List: list of labels.
    """
    return [index_to_class[index] for index in indices]


def format_prob(prob: Iterable, index_to_class: Dict) -> Dict:
    """Format probabilities to a dictionary mapping class label to probability.

    Args:
        prob (Iterable): probabilities.
        index_to_class (Dict): mapping between indices and labels.

    Returns:
        Dict: Dictionary mapping class label to probability.
    """
    d = {}
    for i, item in enumerate(prob):
        d[index_to_class[i]] = item
    return d


def predict_with_proba(
    df: pd.DataFrame,
    predictor: ray.train.torch.torch_predictor.TorchPredictor,
) -> List:  # pragma: no cover, tested with inference workload
    """Predict tags (with probabilities) for input data from a dataframe.

    Args:
        df (pd.DataFrame): dataframe with input features.
        predictor (ray.train.torch.torch_predictor.TorchPredictor): loaded predictor from a checkpoint.

    Returns:
        List: list of predicted labels.
    """
    preprocessor = predictor.get_preprocessor()
    z = predictor.predict(data=df)["predictions"]
    y_prob = torch.tensor(np.stack(z)).softmax(dim=1).numpy()
    results = []
    for i, prob in enumerate(y_prob):
        tag = decode([z[i].argmax()], preprocessor.index_to_class)[0]
        results.append({"prediction": tag, "probabilities": format_prob(prob, preprocessor.index_to_class)})
    return results


def get_best_checkpoint(run_id: str) -> TorchCheckpoint:  # pragma: no cover, mlflow logic
    """Get the best checkpoint from a specific run.

    Args:
        run_id (str): ID of the run to get the best checkpoint from.

    Returns:
        TorchCheckpoint: Best checkpoint from the run.
    """
    artifact_dir = urlparse(mlflow.get_run(run_id).info.artifact_uri).path  # get path from mlflow
    results = Result.from_path(artifact_dir)
    return results.best_checkpoints[0][0]


def predict(
    run_id: str = None,
    title: str = None,
    description: str = None,
) -> Dict:  # pragma: no cover, tested with inference workload
    """Predict the tag for a project given it's title and description.

    Args:
        run_id (str): id of the specific run to load from. Defaults to None.
        title (str, optional): project title. Defaults to "".
        description (str, optional): project description. Defaults to "".

    Returns:
        Dict: prediction results for the input data.
    """
    # Load components
    best_checkpoint = get_best_checkpoint(run_id=run_id)
    predictor = TorchPredictor.from_checkpoint(best_checkpoint)

    # Predict
    sample_df = pd.DataFrame([{"title": title, "description": description, "tag": "other"}])
    results = predict_with_proba(df=sample_df, predictor=predictor)
    logger.info(json.dumps(results, cls=NumpyEncoder, indent=2))
    return results
