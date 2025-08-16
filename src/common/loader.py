"""Generic file loading functions."""

from os.path import isfile, isdir
from glob import glob

import yaml
from easydict import EasyDict


############################################################
# Lambda functions
############################################################
ls_all = lambda path: [path for path in sorted(glob(f"{path}/*"))]
ls_dir = lambda path: [path for path in sorted(glob(f"{path}/*")) if isdir(path)]
ls_file = lambda path: [path for path in sorted(glob(f"{path}/*")) if isfile(path)]


def load_yaml(path: str) -> EasyDict:
    """Load yaml file."""
    with open(path, "r", encoding="utf8") as f:
        config = yaml.safe_load(f)
    return EasyDict(config)
