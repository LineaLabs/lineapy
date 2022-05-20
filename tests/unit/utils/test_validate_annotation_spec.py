import tempfile
from pathlib import Path

import pytest
import yaml

from lineapy.utils.validate_annotation_spec import validate_spec


def test_validate_unsafe_spec():
    valid_yaml = """
-- invalid stuff:: ;
- module: keras.engine.training
  annotations:
    - criteria:
        class_method_name: compile
        class_instance: Model
      side_effects:
        - mutated_value:
            self_ref: SELF_REF
    """

    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(valid_yaml.encode())
        f.flush()
        with pytest.raises(yaml.YAMLError):
            invalid_specs = validate_spec(Path(f.name))


def test_validate_invalid_spec():
    valid_yaml = """
- module: keras.engine.training
  annotations_bug:
    - criteria:
        class_method_name: compile
        class_instance: Model
      side_effects:
        - mutated_value:
            self_ref: SELF_REF
    """

    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(valid_yaml.encode())
        f.flush()
        invalid_specs = validate_spec(Path(f.name))
        assert len(invalid_specs) == 1


def test_validate_valid_spec():
    valid_yaml = """

- module: keras.engine.training
  annotations:
    - criteria:
        class_method_name: compile
        class_instance: Model
      side_effects:
        - mutated_value:
            self_ref: SELF_REF
    """

    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(valid_yaml.encode())
        f.flush()
        invalid_specs = validate_spec(Path(f.name))
        assert len(invalid_specs) == 0
