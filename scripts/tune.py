import hydra
import ray
from omegaconf import DictConfig

from madewithml.tune import tune_models


@hydra.main(version_base=None, config_path="../conf", config_name="tune")
def main(cfg: DictConfig):
    tune_models(**cfg)


if __name__ == "__main__":  # pragma: no cover, application
    if ray.is_initialized():
        ray.shutdown()
    ray.init()
    main()
