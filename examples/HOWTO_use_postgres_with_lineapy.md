# How to Use Postgres with `lineapy`

In this short tutorial, we are going to demonstrate how to use Postgres as your `lineapy` database.

## Requirement

* Docker

## Steps

The easiest way to use postgres with `lineapy` is through Docker.
You can spin up a postgres instance with Docker using following command

```
docker run \
  --name lineaPostgres \                # Container name in docker
  -p 5432:5432 \                        # Expose postgres at port 5432
  -e POSTGRES_USER=postgresuser \       # Preset username as postgresuser
  -e POSTGRES_PASSWORD=postgrespwd \    # Preset password as postgrespws
  -e POSTGRES_DB=postgresdb \           # Preset database name as postgresdb
  -d postgres                           # Official Postgres docker image name
```

You can valid with following command to see whether you have successfully start your postgres or not.

```
docker ps -a | grep lineaPostgres
```

Then expose your postgres connection string into environmental variable `LINEA_DATABASE_URL`

```
export LINEA_DATABASE_URL=postgresql://postgresuser:postgrespwd@localhost:5432/postgresdb
```

Finally, you can use common lineapy cli tool as usual.

```
lineapy [OPTIONS] COMMAND [ARGS]...
```

For instance, we can launch ipython instance with

```
lineapy ipython
```

You can valid you are using Postgres backend in ipython `lineapy ipython` with following command

```
from lineapy.db.db import RelationalLineaDB
RelationalLineaDB.from_environment().url
```

and you should see something like

```
Python 3.9.11 (main, Mar 28 2022, 10:10:35)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.31.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: from lineapy.db.db import RelationalLineaDB
   ...: RelationalLineaDB.from_environment().url
Out[1]: 'postgresql://postgresuser:postgrespwd@localhost:5432/postgresdb'
```

if you are still using SQLite, you should see something similar to

```
Python 3.9.11 (main, Mar 28 2022, 10:10:35)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.31.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: from lineapy.db.db import RelationalLineaDB
   ...: RelationalLineaDB.from_environment().url
Out[1]: 'sqlite:///.linea/db.sqlite'
```
