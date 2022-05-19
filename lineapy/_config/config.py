import logging
import os
import toml
from pathlib import Path

from typing import Any
from enum import Enum

_global_config: dict[str, Any] = {}

# Default Config (all other config should be able to derive from here)
_config = dict(
  home_dir = f"{os.environ.get('HOME','~')}/.lineapy",
  artifact_storage_backend = 'local',
  do_not_track = False,
  logging_level = 'INFO'
)

print(toml.dumps(_config))
# with open(f"{_config['home_dir']}/lineapy_config.toml" ,'w') as f:
#   toml.dump(_config, f)

## config file
config_file_path = Path(os.environ.get('LINEAPY_HOME_DIR', f"{os.environ.get('HOME','~')}/.lineapy")).joinpath('lineapy_config.toml')
if config_file_path.exists():
  _read_config = toml.load(config_file_path)
else:
  config_file_path = Path(os.environ.get('HOME','~')).joinpath('lineapy_config.toml')
  if config_file_path.exists():
    _read_config = toml.load(config_file_path)
  else:
    _read_config = {}


print('default config')
print(_config)

for k, v in _read_config.items():
  _config[k] = v

print('after reading config')
print(_config)

## environmental_variables

var_names = [
  'home_dir',
  'artifact_database_connection_string',
  'artifact_storage_backend',
  'artifact_storage_dir',
  'customized_annotation_folder',
  'do_not_track',
  'logging_level',
  'logging_file',
  'artifact_aws_s3_bucket',
  'artifact_aws_s3_bucket_prefix',
  'ipython_dir'
]
for var_name in var_names:
  env_var_value = os.environ.get(f'LINEAPY_{var_name.upper()}')
  if env_var_value is not None:
    _config[var_name] = env_var_value

print('after environment variables')
print(_config)

