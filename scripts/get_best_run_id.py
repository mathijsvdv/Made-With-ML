import hydra
from omegaconf import DictConfig

from madewithml import utils


@hydra.main(version_base=None, config_path="../conf", config_name="get_best_run_id")
def main(cfg: DictConfig):
    utils.get_best_run_id(**cfg)


if __name__ == "__main__":  # pragma: no cover, application
    main()
