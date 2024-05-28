# Development

## Database

Install postgres, then open a `psql` shell as admin and run the following SQL.
Replace the password with your own password.

```sql
CREATE USER vancelle WITH PASSWORD '00000000-0000-0000-0000-000000000000';
CREATE DATABASE vancelle OWNER vancelle;
```

You probably need to find and edit `pg_hba.conf` to allow network connections.
This will be in the postgres data directory.

```
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

## Configuration

Create `.env`

```shell
VANCELLE_PLEX_TOKEN="<plex token extracted from requests>"
VANCELLE_SECRET_KEY="<random secret key for cookies>"
VANCELLE_SQLALCHEMY_DATABASE_URI="postgresql+psycopg://vancelle:00000000-0000-0000-0000-000000000000@localhost/vancelle"
VANCELLE_STEAM_WEB_API_KEY="<steam web api key>"
VANCELLE_TMDB_API_KEY="<tmdb api key>"
VANCELLE_TMDB_READ_ACCESS_TOKEN="<tmdb read access jwt>"
```

## Database

Create the database scheme.

```shell
flask db upgrade
```

Create a user to log in to the web interface with.

```shell
flask user create
```
