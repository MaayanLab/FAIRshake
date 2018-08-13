# FAIRshake

A web interface for the scoring of biomedical digital objects by user evaluation according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability.

Available at http://fairshake.cloud/

## Code Layout
- FAIRshake: The django project settings
- FAIRshakeHub: The website itself, gets all of its information from FAIRshakeAPI
- FAIRshakeAPI: The primary API facilitator, is enabled with the other API components

## Development

### Setup
Python 3 is required to run this project.

Install all dependencies into your environment.
```bash
pip install -r requirements.txt
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

## Production
### Secret values
For the docker-compose to work properly in production, `/ssl/` should have the following files:
- `my.cnf`: mysql configuration file with production database credentials
- `secret.txt`: Secret key for production (random private string of characters)
- `cert.key`: SSL Private Key
- `cert.crt`: SSL CA Signed Public Key

### Docker deployment
```bash
docker-compose up
````
