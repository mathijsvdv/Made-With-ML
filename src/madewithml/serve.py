from http import HTTPStatus
from typing import Dict

import pandas as pd
import ray.serve as serve
from fastapi import FastAPI
from ray.train.torch import TorchPredictor
from starlette.requests import Request

from madewithml import evaluate, predict
from madewithml.config import MLFLOW_TRACKING_URI, mlflow

# Define application
app = FastAPI(
    title="Made With ML",
    description="Classify machine learning projects.",
    version="0.1",
)


@serve.deployment(route_prefix="/", num_replicas="1", ray_actor_options={"num_cpus": 8, "num_gpus": 0})
@serve.ingress(app)
class ModelDeployment:
    def __init__(self, run_id: str, threshold: int = 0.9):
        """Initialize the model."""
        self.run_id = run_id
        self.threshold = threshold
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)  # so workers have access to model registry
        best_checkpoint = predict.get_best_checkpoint(run_id=run_id)
        self.predictor = TorchPredictor.from_checkpoint(best_checkpoint)
        self.preprocessor = self.predictor.get_preprocessor()

    @app.get("/")
    def _index(self) -> Dict:
        """Health check."""
        response = {
            "message": HTTPStatus.OK.phrase,
            "status-code": HTTPStatus.OK,
            "data": {},
        }
        return response

    @app.get("/run_id/")
    def _run_id(self) -> Dict:
        """Get the run ID."""
        return {"run_id": self.run_id}

    @app.post("/evaluate/")
    async def _evaluate(self, request: Request) -> Dict:
        data = await request.json()
        results = evaluate.evaluate(run_id=self.run_id, dataset_loc=data.get("dataset"))
        return {"results": results}

    @app.post("/predict/")
    async def _predict(self, request: Request) -> Dict:
        # Get prediction
        data = await request.json()
        df = pd.DataFrame([{"title": data.get("title", ""), "description": data.get("description", ""), "tag": ""}])
        results = predict.predict_with_proba(df=df, predictor=self.predictor)

        # Apply custom logic
        for i, result in enumerate(results):
            pred = result["prediction"]
            prob = result["probabilities"]
            if prob[pred] < self.threshold:
                results[i]["prediction"] = "other"

        return {"results": results}
