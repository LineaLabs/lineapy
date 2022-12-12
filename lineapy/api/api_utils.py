import logging
import pickle
import re
from pathlib import Path

from pandas.io.pickle import read_pickle
from pandas.io.pickle import to_pickle as pandas_pickle

from lineapy.db.db import RelationalLineaDB
from lineapy.utils.analytics.event_schemas import ErrorType, ExceptionEvent
from lineapy.utils.analytics.usage_tracking import track
from lineapy.utils.config import options

logger = logging.getLogger(__name__)


def de_lineate_code(code: str, db: RelationalLineaDB) -> str:
    """
    De-linealize the code by removing any lineapy api references
    """
    lineapy_pattern = re.compile(
        r"(lineapy.(save\(([\w]+),\s*[\"\']([\w\-\s]+)[\"\']\)|get\([\"\']([\w\-\s]+)[\"\']\).get_value\(\)))"
    )
    # init swapped version

    def replace_fun(match):
        if match.group(2).startswith("save"):
            # FIXME - there is a potential issue here because we are looking up the artifact by name
            # This does not ensure that the same version of current artifact is being looked up.
            # We support passing a version number to the get_artifactorm_by_name but it needs to be parsed
            # out in the regex somehow. This would be simpler when we support named versions when saving.
            dep_artifact = db.get_artifactorm_by_name(match.group(4))
            path_to_use = db.get_node_value_path(
                dep_artifact.node_id, dep_artifact.execution_id
            )
            return f'pickle.dump({match.group(3)},open("{path_to_use}","wb"))'

        elif match.group(2).startswith("get"):
            # this typically will be a different artifact.
            dep_artifact = db.get_artifactorm_by_name(match.group(5))
            path_to_use = db.get_node_value_path(
                dep_artifact.node_id, dep_artifact.execution_id
            )
            return f'pickle.load(open("{path_to_use}","rb"))'

    swapped, replaces = lineapy_pattern.subn(replace_fun, code)
    if replaces > 0:
        # If we replaced something, pickle was used so add import pickle on top
        # Conversely, if lineapy reference was removed, potentially the import lineapy line is not needed anymore.
        remove_pattern = re.compile(r"import lineapy\n")
        match_pattern = re.compile(r"lineapy\.(.*)")
        swapped = "import pickle\n" + swapped
        if match_pattern.search(swapped):
            # we still are using lineapy.xxx functions
            # so do nothing
            pass
        else:
            swapped, lineareplaces = remove_pattern.subn("\n", swapped)
            # logger.debug(f"Removed lineapy {lineareplaces} times")

    # logger.debug("replaces made: %s", replaces)

    return swapped


def to_pickle(
    value,
    filepath_or_buffer,
    storage_options=None,
):
    pandas_pickle(
        obj=value,
        filepath_or_buffer=filepath_or_buffer,
        compression="infer",
        protocol=pickle.HIGHEST_PROTOCOL,
        storage_options=storage_options,
    )


def _read_pickle(pickle_filename):
    """
    Read pickle file from artifact storage dir
    """
    # TODO - set unicode etc here
    artifact_storage_dir = options.safe_get("artifact_storage_dir")
    filepath = (
        artifact_storage_dir.joinpath(pickle_filename)
        if isinstance(artifact_storage_dir, Path)
        else f'{artifact_storage_dir.rstrip("/")}/{pickle_filename}'
    )
    try:
        logger.debug(
            f"Retriving pickle file from {filepath} ",
        )
        return read_pickle(
            filepath, storage_options=options.get("storage_options")
        )
    except Exception as e:
        logger.error(e)
        track(
            ExceptionEvent(
                ErrorType.RETRIEVE, "Error in retriving pickle file"
            )
        )
        raise e
