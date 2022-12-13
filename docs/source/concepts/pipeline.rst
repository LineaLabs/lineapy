.. _pipeline_concept:

Pipeline
========

In the context of data science, a pipeline refers to a series of steps that transform data into useful
information/product. For instance, a common end-to-end machine learning pipeline includes data preprocessing, model training, and model evaluation steps. These pipelines are often developed one component at a time.
Once the individual components are developed, they are connected to form an end-to-end pipeline.

In LineaPy, each component is represented as an artifact, and LineaPy provides APIs to create pipelines from a group of artifacts. These pipelines can then be run through specific orchestration engines to handle new data.

Note that the pipelines created by LineaPy are meant to be reviewed and accepted by developers before they go into production, and we provide mechanisms to verify the generated pipelines in the development environment for validation.

.. include:: /snippets/docs_feedback.rstinc
