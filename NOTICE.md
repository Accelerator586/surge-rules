# Sources and modifications

The snapshots in `vendor/sukka/` originate from [SukkaW/Surge](https://github.com/SukkaW/Surge), authored and maintained by Sukka and contributors, under GNU AGPL version 3. The full license is in `LICENSE`.

Initial generated snapshot: `SukkaLab/ruleset.skk.moe@fa49240ecc8567c79319ff347e8cd04c9b940939`, built from `SukkaW/Surge@d46d9ca1a28e74f2a40f6c0bae93569f85c3aa75`. That generated GitHub mirror is marked archived; it is used only for reproducible initial import. Future update proposals fetch the official Ruleset Server URLs recorded in `sources.lock.json`, not the archived mirror.

Modified distribution: keep only DOMAIN and DOMAIN-SUFFIX rules; remove the upstream identification domain; omit broad public suffix and shared-cloud entries listed in `policy.json`; omit the shared GitHub API hostname from the AI source; add the public service rules in `rules/`; deduplicate and sort. No upstream process, keyword, URL, or IP rule enters the generated service lists.

The repository's scripts, documentation, additions, and generated distributions are provided under GNU AGPL version 3. Source bytes and SHA-256 hashes are retained so the published lists can be reproduced offline.
