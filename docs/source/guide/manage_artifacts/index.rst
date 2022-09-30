Artifact Storage
================

In LineaPy, an artifact store is a centralized repository for artifacts
(check :ref:`here <artifact_store_concept>` for a conceptual explanation).
Under the hood, it is a collection of two data structures:

- Serialized artifact values (i.e., pickle files)
- Database that stores artifact metadata (e.g., timestamp, version, code, pointer to the serialized value)

Encapsulating both value and code, as well as other metadata such as creation time and version,
LineaPy's artifact store provides a more unified and streamlined experience to save, manage, and reuse
works from different people over time. Contrast this with a typical setup where the team stores their
outputs in one place (e.g., a Key Value store) and the code in another (e.g., GitHub repo) --- we can
imagine how difficult it would be to maintain correlations between the two. LineaPy simplifies lineage tracking by storing all correlations in one framework: artifact store.

.. note::

   By default, the serialized values and the metadata are stored in ``.lineapy/linea_pickles/``
   and ``.lineapy/db.sqlite``, respectively, where ``.lineapy/`` is created under
   the system's home directory.

   This default location can be overridden by modifying the configuration file:

   .. code:: json

      {
         "artifact_storage_dir": [NEW-PATH-TO-STORE-SERIALIZED-VALUES],
         "database_url": [NEW-DATABASE-URL-FOR-STORING-METADATA],
         ...
      }

   or making these updates in each interactive session:

   .. code:: python

      lineapy.options.set('artifact_storage_dir', [NEW-PATH-TO-STORE-SERIALIZED-VALUES])
      lineapy.options.set('database_url', [NEW-DATABASE-URL-FOR-STORING-METADATA])
   
   Read more about configuration :ref:`here <configurations>`.

.. toctree::
   :maxdepth: 1

   artifact_reuse
   storage_location/index
