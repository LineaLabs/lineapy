Changing Storage Location
=========================

Out of the box, LineaPy comes with a local SQLite database.
As the user gets into more serious applications, however, this lightweight database
poses limitations (e.g., single writes).
Accordingly, LineaPy supports other storage options such as PostgreSQL.
This support is essential for team collaborations as it enables the artifact store
be hosted in a shared environment that can be accessed by different team members.

.. toctree::
   :maxdepth: 1

   postgres
   s3
