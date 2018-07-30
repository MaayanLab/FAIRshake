# FAIRshake

A web interface for the scoring of biomedical digital objects by user evaluation according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability.

Available at http://fairshake.cloud/

## Code Layout
- FAIRshake: The django project settings
- FAIRshakeHub: The website itself, gets all of its information from FAIRshakeAPI
- FAIRshakeAPI: The primary API facilitator, is enabled with the other API components

## Development
### Django Shell
ipython is recommended: `pip install ipython`
`./manage.py shell`

### Django Live Reloading Server
In separate terminals execute these commands and then navigate to <http://localhost:8000/>.
```python
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
- `cert.crt`
- `my.cnf`
- `cert.key`

### Docker deployment
```bash
docker-compose up
````
