import hydra
from omegaconf import DictConfig

from madewithml.predict import predict


@hydra.main(version_base=None, config_path="../conf", config_name="predict")
def main(cfg: DictConfig):
    predict(**cfg)


if __name__ == "__main__":  # pragma: no cover, application
    main()
