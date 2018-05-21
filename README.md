# FAIRshake

A web interface for the scoring of biomedical digital objects by user evaluation according to the FAIR data principles: Findability, Accessibility, Interoperability, and Reusability.

Available at http://fairshake.cloud/

## Code Layout
- FAIRshake: The django project settings
- FAIRshakeHub: The website itself, gets all of its information from FAIRshakeAPI
- FAIRshakeAPI: The primary API facilitator, is enabled with the other API components
- FAIRshakeInsignia: A score display API
- FAIRshakeAssessment: A manual assessment API
- FAIRshakeRubric: A rubric provider

## Development
### Django Shell
ipython is recommended: `pip install ipython`

`./manage.py shell`
