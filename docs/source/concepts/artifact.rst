.. _artifact_concept:

Artifact
========

In LineaPy, an artifact refers to any intermediate result from the development process. Most often, an artifact
manifests as a variable that stores data in a specific state (e.g., ``my_num = your_num + 10``). In the data science
workflow, an artifact can be a model, a chart, a statistic, or a dataframe, or a feature function.

What makes LineaPy special is that it treats an artifact as both code and value. That is, when storing an artifact,
LineaPy not only records the state (i.e., value) of the variable but also traces and saves all relevant operations
leading to this state --- as code. Such a complete development history or *lineage* then allows LineaPy to fully reproduce
the given artifact. Furthermore, it provides the ground to automate data engineering work to bring data science from development to production.
