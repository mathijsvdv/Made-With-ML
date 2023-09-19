import hydra
from omegaconf import DictConfig

from madewithml.evaluate import evaluate


@hydra.main(version_base=None, config_path="../conf", config_name="evaluate")
def main(cfg: DictConfig):
    evaluate(**cfg)


if __name__ == "__main__":  # pragma: no cover, application
    main()
