## Result

Describe the affected service and resulting routing group.

## Direct-access changes

List new CN / Apple / Parsec direct domains and why they belong here. State explicitly when there are none.

## Validation

- [ ] `python3 scripts/rules.py build` and `python3 scripts/rules.py check`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Unknown-domain and lookalike-domain cases still use FINAL proxy
- [ ] Public rules contain no personal configuration or credentials
