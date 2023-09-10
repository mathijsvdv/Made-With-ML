import argparse

import ray
import ray.serve as serve

from madewithml.serve import ModelDeployment

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", help="run ID to use for serving.")
    parser.add_argument("--threshold", type=float, default=0.9, help="threshold for `other` class.")
    args = parser.parse_args()
    ray.init()
    serve.run(ModelDeployment.bind(run_id=args.run_id, threshold=args.threshold))
