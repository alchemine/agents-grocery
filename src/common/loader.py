"""Generic file loading functions."""

from os.path import isfile, isdir
from glob import glob


############################################################
# Lambda functions
############################################################
ls_all = lambda path: [path for path in sorted(glob(f"{path}/*"))]
ls_dir = lambda path: [path for path in sorted(glob(f"{path}/*")) if isdir(path)]
ls_file = lambda path: [path for path in sorted(glob(f"{path}/*")) if isfile(path)]
