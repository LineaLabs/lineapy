# How to Use Postgres with `lineapy`

In this short tutorial, we are going to demonstrate how to use Postgres as your `lineapy` database.

## Requirement

* Docker

## Steps

The easiest way to use postgres with `lineapy` is through Docker.
You can spin up a postgres instance with Docker using following command

```
docker run --name lineaPostgres -p 5432:5432 -e POSTGRES_USER=postgresuser -e POSTGRES_PASSWORD=postgrespwd -e POSTGRES_DB=postgresdb -d postgres 
```

where

* `--name lineaPostgres`: make the container name as *lineaPostgres* in docker
* `-p 5432:5432`: expose postgres at port 5432
* `-e POSTGRES_USER=postgresuser`: set username as postgresuser
* `-e POSTGRES_PASSWORD=postgrespwd`: set password as postgrespws
* `-e POSTGRES_DB=postgresdb`: set database name as postgresdb
* `-d postgres`: official postgres docker image name

You can valid with following command to see whether you have successfully start your postgres or not.

```
docker ps -a | grep lineaPostgres
```

Then export your postgres connection string into environmental variable `LINEA_DATABASE_URL` before using `lineapy`

```
export LINEA_DATABASE_URL=postgresql://postgresuser:postgrespwd@localhost:5432/postgresdb
```

Finally, you can use common lineapy cli tool as usual.
If you install `lineapy` in a venv or a conda environment, make you've changed to that environment.

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
