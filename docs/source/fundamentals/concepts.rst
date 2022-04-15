.. _concepts:

Concepts
========

Artifact
--------

In LineaPy, an artifact refers to any intermediate result from the development process. Most often, an artifact
manifests as a variable that stores data in a specific state (e.g., ``my_num = your_num + 10``). In the data science
workflow, an artifact can be a model, a chart, a statistic, a dataframe, or a feature function.

What makes LineaPy special is that it treats an artifact as both code and value. That is, when storing an artifact,
LineaPy not only records the state (i.e. value) of the variable but also traces and saves all relevant operations
leading to this state --- as code. Such a complete development history or *lineage* then allows LineaPy to fully reproduce
the given artifact. Furthermore, it provides the ground to automate certain code transformations (e.g., building
pipelines that can be scheduled and monitored), which reduces the gap between development and production.

Artifact Store
--------------

LineaPy saves artifacts in the artifact store, which is a centralized repository for artifacts and
their metadata (e.g., creation time, session ID). LineaPy's artifact store is globally accessible, which means
the user can view, load, and build on artifacts across different development sessions and even different projects.
Given the organic and iterative nature of data science work, this type of unified global storage is likely to
accelerate the overall development process. Moreover, it can facilitate collaboration between different teams
as it provides a single source of truth for all prior relevant work.

Pipeline
--------

In the context of data science, a pipeline refers to a series of processes that transform data into useful
information/product. For instance, a critical part of data science is training models that can make intelligent
predictions. Model building can be viewed as a pipeline as it involves a set of transformations onto the raw data,
including 1) pre-processing and 2) model training.

[[ Add a diagram showing transition from raw data to transformed data to model ]]

Note that this pipeline is subject to multiple revisions in practice: we may want to use a new feature that can boost
model performance, in which case we will need to update pre-processing and model training steps accordingly. Or, we may
discover a better modeling strategy/framework to use, in which case we will need to refactor the pipeline as well.
Even with the “best” model, it may eventually become outdated as the world and its data change (an issue known as
“model drift”) and we may need to redesign the existing pipeline.

In general, data science workflows revolve around building and refining pipelines of this sort.
