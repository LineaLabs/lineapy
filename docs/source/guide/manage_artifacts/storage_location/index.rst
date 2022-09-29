Changing Storage Location
=========================

Out of the box, LineaPy comes with a local SQLite database for a quick start.
As the user gets into more serious applications, however, this lightweight database
poses limitations (e.g., single write access to a database at a time).
Accordingly, LineaPy supports other storage options such as PostgreSQL and S3.
This support is essential to team collaboration because it demands the artifact store
be hosted in a shared environment that can be accessed by different team members.

.. toctree::
   :maxdepth: 1

   postgres
   s3
