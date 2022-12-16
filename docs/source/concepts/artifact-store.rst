.. _concept_artifact_store:

Artifact Store
==============

LineaPy saves artifacts in the artifact store, which is a centralized repository for artifacts and
their metadata (e.g., creation time, version). Under the hood, it is a collection of two data structures:

- Serialized artifact values (i.e., pickle files)
- Database that stores artifact metadata (e.g., timestamp, version, code, pointer to the serialized value)

Encapsulating both value and code, as well as other metadata such as creation time and version,
LineaPy's artifact store provides a more unified and streamlined experience to save, manage, and reuse
works from different people over time. Contrast this with a typical setup where the team stores their
outputs in one place (e.g., a key-value store) and the code in another (e.g., GitHub repo) --- we can
imagine how difficult it would be to maintain correlations between the two. LineaPy simplifies lineage tracking
by storing all correlations in one framework: artifact store.

LineaPy's artifact store is globally accessible, which means the user can view, load, and build on artifacts across
different development sessions and even different projects. This unified global storage is designed to accelerate the overall
development process, which is iterative in nature. Moreover, it can facilitate collaboration between different teams
as it provides a single source of truth for all prior relevant work.

.. include:: /snippets/docs_feedback.rstinc
