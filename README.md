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

### Build Docker
```bash
docker build -t fairshake .
```

## Production
### Environment variables

```bash
MYSQL_CONFIG=/path/to/my.cnf
SECRET_KEY=custom_generated_secret_key
```
### Docker deployment
```bash
docker run \
  -p 80:80 \
  -p 443:443 \
  -v my.cnf:/my.cnf \
  -v ssl:/ssl \
  -it fairshake
```

- `my.cnf` should be a mysql configuration to connect to the database
- `ssl` should be a directory with `cert.key` and `cert.crt` ssl certificates.
