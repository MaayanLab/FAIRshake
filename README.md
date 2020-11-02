# FAIRshake

A web interface for the scoring of biomedical digital objects by user evaluation according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability.

Available at http://fairshake.cloud/

## Code Layout
- FAIRshake: The django project settings
- FAIRshakeHub: The website itself, gets all of its information from FAIRshakeAPI
- FAIRshakeAPI: The primary API facilitator, is enabled with the other API components
- extensions: Extensions to dependent libraries

## Development

### Setup
Python 3 is required to run this project.

Install all dependencies into your environment.
```bash
pip install -r requirements.txt
```

Note that `mysqlclient` is the recommended client but `pymysql` can be used as a fallback.

### Staticfiles collection
To render the page properly in development, it's necessary to collect staticfiles so they can be hosted by django.
```bash
./manage.py collectstatic
```

### Environment setup
```bash
# Run in debugging mode, show errors and host staticfiles locally
export DEBUG=1

# Specify location of mysql config file for production database
export MYSQL_CONFIG=$(pwd)/config/my.cnf
```

### Django Shell
ipython is recommended: `pip install ipython`
`./manage.py shell`

### Django Live Reloading Server
In separate terminals execute these commands and then navigate to <http://localhost:8000/>.
```bash
./manage.py runserver
./manage.py livereload
```

### Build Docker
```bash
docker-compose build
```

### Database migrations
Django keeps track of database migrations. When modifying `models` it is imperative to create and apply migrations on all old databases. Migrations can be safely removed if they have been applied to all independent databases (for that reason, it's probably better to just not remove them).
```bash
./manage.py makemigrations
./manage.py migrate
```

Note that this will try but not always succeed to detect renamed fields and such and migrate the backend database accordingly. If it is unable to, it may require manual intervention. For more information https://docs.djangoproject.com/en/2.0/topics/migrations/.

### Testing
```bash
# Run Tests
./manage.py test
# Run Tests with Coverage
coverage run --source='.' manage.py test && coverage report
```

## Database Backup & Restore
### Backup
```bash
# Backup data, omit django internals (which could cause loading to fail)
./manage.py dumpdata \
  -e contenttypes \
  -e admin \
  -e auth.Permission \
  --natural-foreign \
  --indent=2 \
    > mybackup.json
```

### Restore
```bash
# Ensure database is initialized
./manage.py migrate
# Load data from backup
./manage.py loaddata mybackup.json
```

## Production
### Secret values
For the docker-compose to work properly in production, `/config/` should have the following files:
- `my.cnf`: mysql configuration file with production database credentials
  - This file can be specified with `MYSQL_CONFIG` environment variable
- `secret.txt`: Secret key for production (random private string of characters)
- `cert.key`: SSL Private Key (optional, for https)
- `cert.crt`: SSL CA Signed Public Key (optional, for https)

### Email
Can be configured by the administrator [here](http://localhost:8000/admin/des/dynamicemailconfiguration/). If using gmail, ensure you [allow less secure apps](https://myaccount.google.com/lesssecureapps).

### Docker deployment
```bash
docker-compose up
```

## Troubleshooting

### MySQL issues
Errors involving mysql trying to load from /tmp/sock arrise when `MYSQL_CONFIG` environment variable is being read, but the file on the other end is problematic.
1. You're not using an absolute path, so django, running perhaps elsewhere, can't find it. Try: `export MYSQL_CONFIG=$(pwd)/ssl/my.cnf`
  - Verify that it's accessible at the environment variable with `cat $MYSQL_CONFIG`
2. Your configuration file has loose permissions, Try: `chmod 644 ssl/my.cnf` before trying again.
3. Your configuration is malformed.

### Database issues
In general, if the database has changed (and there are new migration files), if you're running a local database you may need to apply new migrations with `./manage.py migrate`.

#### No Cache Table
If the cache table doesn't yet exist, you can create it with `./manage.py createcachetable`.

### Dependency issues
First try re-executing `pip install -r requirements.txt`.

In the worst case you may need to rebuild your environment from nothing (starting from scratch, and installing dependencies again).

I recommend `pyenv` for managing isolated python environments.
