import hydra
import ray

from madewithml.train import train_model

train_model = hydra.main(version_base=None, config_path="../conf", config_name="train")(train_model)


if __name__ == "__main__":  # pragma: no cover, application
    if ray.is_initialized():
        ray.shutdown()
    ray.init()
    train_model()
