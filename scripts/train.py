import hydra
import ray
from omegaconf import DictConfig

from madewithml.train import train_model


@hydra.main(version_base=None, config_path="../conf", config_name="train")
def main(cfg: DictConfig):
    train_model(**cfg)


if __name__ == "__main__":  # pragma: no cover, application
    if ray.is_initialized():
        ray.shutdown()
    ray.init()
    main()
