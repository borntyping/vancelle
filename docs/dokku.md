Dokku
=====

Deployment
----------

Create and configure the [Dokku](https://dokku.com/) application:

```shell
dokku apps:create vancelle
dokku builder:set vancelle selected dockerfile
dokku docker-options:add vancelle build '--build-arg DART_ARCH=arm64'
dokku postgres:create vancelle
dokku postgres:link vancelle vancelle
dokku config:set --no-restart vancelle POSTGRES_DATABASE_SCHEME=postgresql+psycopg
```

Set secrets:

```shell
 dokku config:set --no-restart vancelle VANCELLE_SECRET_KEY=...
 dokku config:set --no-restart vancelle VANCELLE_STEAM_WEB_API_KEY=...
 dokku config:set --no-restart vancelle VANCELLE_TMDB_API_KEY=...
 dokku config:set --no-restart vancelle VANCELLE_TMDB_READ_ACCESS_TOKEN=...
```

Configure HTTPS (optional). Make sure the files created by `tailscale cert` can be read by the `dokku` user.

```shell
tailscale cert <hostname>
dokku certs:add vancelle <hostname>.crt <hostname>.key
dokku proxy:set vancelle nginx
dokku ports:add vancelle http:80:5000
```

Create a user. Skip this if you plan to import a `vancelle-backup.json` file.

```shell
dokku run vancelle flask user create
```

Managing data
-------------

Export to your local machine:

```shell
ssh <dokku-host> -- docker exec -i vancelle.web.1 poetry run flask data export - > vancelle-backup.json
```

Import from a file on your local machine:

```shell
ssh <dokku-host> -- docker exec -i vancelle.web.1 poetry run flask data import - --dry-run < vancelle-backup.json
```
