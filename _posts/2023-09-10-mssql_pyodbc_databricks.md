---
layout: post
title: Connect From PyODBC to SQL Server in DataBricks Cluster
---

It's a shame that clusters created in Azure DataBricks don't have
the `pyodbc` drivers for Microsoft SQL Server installed by default.  
Perhaps the people who normally use DataBricks don't typically connect to
SQL Server, but it feels that it'd be easier if the images provided
by Microsoft would enable that by default.

Then, to make things more difficult, a lot of the answers on the Internet
on how to install these drivers are for the older versions of DataBricks.  
The newer versions change slighly the approach used to install them.

The gist of the install process is as following:

1. Create an install shell-script to install the `msodbcsql17` package
2. Save it as a file in DataBricks, whether as a _Workspace_ script or
   in a connected repository.
3. When configuring the cluster, add this file as an "init script".

## Install Script

The script below is centered around installing the `msodbcsql17` driver.  
For this, we need to import the Ubuntu sources for `apt` and then install
the package along with the `unixodbc-dev`:

```sh
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install msodbcsql17
apt-get -y install unixodbc-dev
sudo apt-get install python3-pip -y
```

## Saving Script in DataBricks

Save the script as a file, say `pyodb-setup.sh`, in either a DataBricks repository:

![PyODBC Setup File in Connected Repo](/media/images/databricks_init_file_repo.png)

or directly in a _Workspace_ file (in the example below, stored in
`Workspace/Shared/pyodbc-setup.sh`):

![PyODBC Setup File in Workspace Shared Folder](/media/images/databricks_init_file_workspace.png)

## Configure DataBricks Cluster

Either during creation, or after, configure the DataBricks cluster by expanding
the "Advanced Options" section on the "Configuration" tab, then by selecting
the "Init Scripts" tab.  
There will be three options to add a new script:
"Workspace", "ABFSS", and "DBFS".

The "DBFS" is [deprecated](https://learn.microsoft.com/en-us/azure/databricks/init-scripts/cluster-scoped),
and the "ABFSS" (Azure Blob File System or Azure Data Lake Storage Gen) is a bit
more complicated to set up; the "Workspace" approach outlined above is the simplest.

The path to the `pyodbc-setup.sh` script is relative to the root of "Workspace",
so `/Shared/pyodb-init.sh` or
`/Repos/user/repo/pyodb-install.sh` if in the repository.

![Setting up init scripts in DataBricks cluster config](/media/images/databricks_init_file_config.png)

## Connecting

This whole setup allows `pyodbc` to connect to a SQL Server using a connection
string specifying the SQL Server 17 driver,
`"DRIVER=ODBC Driver 17 for SQL Server;..."`,
like so:

```py
server = "example-server.database.windows.net"
db_name = "example-db"
user = "example_user"
pwd = "example password"
conn_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={db_name};UID={user};PWD={pwd}"
conn = pyodbc.connect(conn_string)
with conn:
  conn.execute("select * from table")
```

As a note, there's a newer version, `msodbcsql18` -- see
[here the whole list](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16#ubuntu).  
The script remains the same, save for pointing to a different Ubuntu,
for example: `https://packages.microsoft.com/config/ubuntu/18.04/prod.list`.
