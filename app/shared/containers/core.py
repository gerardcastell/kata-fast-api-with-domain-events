from dependency_injector import containers, providers
import yaml
import pathlib


class Core(containers.DeclarativeContainer):
    config_path = providers.Configuration()  # a path string
    config = providers.Configuration()  # actual config values

    def _load_config(path: str) -> dict:
        return yaml.safe_load(pathlib.Path(path).read_text())

    # load YAML into config
    config_loader = providers.Callable(_load_config, path=config_path)
