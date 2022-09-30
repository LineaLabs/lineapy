.. _concepts:

Concepts
========

.. _artifact_concept:

Artifact
--------

In LineaPy, an artifact refers to any intermediate result from the development process. Most often, an artifact
manifests as a variable that stores data in a specific state (e.g., ``my_num = your_num + 10``). In the data science
workflow, an artifact can be a model, a chart, a statistic, or a dataframe, or a feature function.

What makes LineaPy special is that it treats an artifact as both code and value. That is, when storing an artifact,
LineaPy not only records the state (i.e. value) of the variable but also traces and saves all relevant operations
leading to this state --- as code. Such a complete development history or *lineage* then allows LineaPy to fully reproduce
the given artifact. Furthermore, it provides the ground to automate data engineering work to bring data science from development to production.

.. _artifact_store_concept:

Artifact Store
--------------

LineaPy saves artifacts in the artifact store, which is a centralized repository for artifacts and
their metadata (e.g., creation time, version). LineaPy's artifact store is globally accessible, which means
the user can view, load, and build on artifacts across different development sessions and even different projects.
This unified global storage is designed to accelerate the overall development process, which is iterative in nature.
Moreover, it can facilitate collaboration between different teams
as it provides a single source of truth for all prior relevant work.

.. _pipeline_concept:

Pipeline
--------

In the context of data science, a pipeline refers to a series of steps that transform data into useful
information/product. For instance, a common end-to-end machine learning pipeline includes data preprocessing, model training, and model evaluation steps. These pipelines are often developed one component at a time.
Once the individual components are developed, they are connected to form an end-to-end pipeline.

In LineaPy, each component is represented as an artifact, and LineaPy provides APIs to create pipelines from a group of artifacts. These pipelines can then be run through specific orchestration engines to handle new data.

Note that the pipelines created by LineaPy are meant to be reviewed and accepted by developers before they go into production, and we provide mechanisms to verify the generated pipelines in the development environment for validation.
