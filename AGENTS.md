# Maintenance contract

- Repository contains public service rules only. Never read/import a live Surge profile into the repository. Never publish proxy endpoints, credentials, private keys, home domains, private routes, or personal port forwards.
- CN and other generated service lists accept only DOMAIN and DOMAIN-SUFFIX. Do not add DOMAIN-KEYWORD, PROCESS-NAME, GEOIP, IP-ASN, remote RULE-SET imports, or IP ranges to these lists.
- Unknown domains and unmatched public IPs must keep using FINAL -> Proxy. New direct domains require review; never auto-merge upstream updates.
- Edit rules/ for personal additions, vendor/ only through the updater, and regenerate dist/ with python3 scripts/rules.py build. Do not hand-edit dist/.
- Developer console/API exceptions use exact DOMAIN entries in rules/proxy-allow.list and the Developer policy. Every host must have matching, public host-only evidence in developer-sources.json; do not record project IDs, account details, URL tokens, or cookies.
- Preserve source attribution and AGPL-3.0 license. sources.lock.json hashes must match the source snapshots.
- Run python3 scripts/rules.py check and python3 -m unittest discover -s tests -v before proposing changes. On macOS, additionally check the generated profile using surge-cli --check when available.
- If GitHub Actions or tokens cannot create a PR, report the specific permission issue. Never make direct main-branch updates as a fallback for upstream maintenance.
