import base64
import errno
import os
from typing import Optional

from hera import Artifact, ImagePullPolicy, set_global_task_image
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService
from kubernetes import client, config


def get_sa_token(
    service_account: str,
    namespace: str = "argo",
    config_file: Optional[str] = None,
):
    """
    Configues the kubernetes client and returns the service account token for the
    specified service account in the specified namespace.
    This is used in the case the local kubeconfig exists.
    """
    if config_file is not None and not os.path.isfile(config_file):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_file)

    config.load_kube_config(config_file=config_file)
    v1 = client.CoreV1Api()
    if v1.read_namespaced_service_account(service_account, namespace).secrets is None:
        print("No secrets found in namespace: %s" % namespace)
        return "None"

    secret_name = (
        v1.read_namespaced_service_account(service_account, namespace).secrets[0].name
    )

    sec = v1.read_namespaced_secret(secret_name, namespace).data
    return base64.b64decode(sec["token"]).decode()


def task_run_session_including_iris_preprocessed(url, test_size, random_state):
    import pathlib
    import pickle

    import iris_pipeline_module

    url = str(url)

    test_size = float(test_size)

    random_state = int(random_state)

    artifacts = iris_pipeline_module.run_session_including_iris_preprocessed(
        url, test_size, random_state
    )

    iris_preprocessed = artifacts["iris_preprocessed"]
    iris_model = artifacts["iris_model"]
    iris_model_evaluation = artifacts["iris_model_evaluation"]

    if not pathlib.Path("/tmp").joinpath("").exists():
        pathlib.Path("/tmp").joinpath("").mkdir()
    pickle.dump(
        iris_preprocessed, open("/tmp//variable_iris_preprocessed.pickle", "wb")
    )

    if not pathlib.Path("/tmp").joinpath("").exists():
        pathlib.Path("/tmp").joinpath("").mkdir()
    pickle.dump(iris_model, open("/tmp//variable_iris_model.pickle", "wb"))

    if not pathlib.Path("/tmp").joinpath("").exists():
        pathlib.Path("/tmp").joinpath("").mkdir()
    pickle.dump(
        iris_model_evaluation, open("/tmp//variable_iris_model_evaluation.pickle", "wb")
    )


def task_setup():
    import pathlib
    import pickle

    import iris_pipeline_module

    pass


def task_teardown():
    import pathlib
    import pickle

    import iris_pipeline_module

    pass


ws = WorkflowService(
    host="https://localhost:2746",
    verify_ssl=False,
    token=get_sa_token("argo", "argo", os.path.expanduser("~/.kube/config")),
    namespace="argo",
)

with Workflow("iris-pipeline", service=ws) as w:

    set_global_task_image("iris_pipeline:lineapy")

    run_session_including_iris_preprocessed = Task(
        "run-session-including-iris-preprocessed",
        task_run_session_including_iris_preprocessed,
        [
            {
                "url": "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
                "test_size": "0.33",
                "random_state": "42",
            }
        ],
        image_pull_policy=ImagePullPolicy.Never,
        outputs=[
            Artifact(
                "iris_preprocessed",
                "/tmp/iris_pipeline/variable_iris_preprocessed.pickle",
            ),
            Artifact(
                "iris_model",
                "/tmp/iris_pipeline/variable_iris_model.pickle",
            ),
            Artifact(
                "iris_model_evaluation",
                "/tmp/iris_pipeline/variable_iris_model_evaluation.pickle",
            ),
        ],
    )

    setup = Task(
        "setup",
        task_setup,
        image_pull_policy=ImagePullPolicy.Never,
    )

    teardown = Task(
        "teardown",
        task_teardown,
        image_pull_policy=ImagePullPolicy.Never,
    )

    setup >> run_session_including_iris_preprocessed

    run_session_including_iris_preprocessed >> teardown


w.create()
