# Development

## Database

Install postgres, then open a `psql` shell as admin and run the following SQL.
Replace the password with your own password.

```sql
CREATE USER vancelle WITH PASSWORD '00000000-0000-0000-0000-000000000000';
CREATE DATABASE vancelle OWNER vancelle;
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
