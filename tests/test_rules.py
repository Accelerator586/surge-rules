import importlib.util
import contextlib
import io
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rules", ROOT / "scripts/rules.py")
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)


class RulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy, cls.groups, _ = rules.collect()

    def test_expected_services(self):
        cases = {"juejin.cn": "cn-allow", "api.juejin.cn": "cn-allow",
                 "www.baidu.com": "cn", "www.jd.com": "cn", "www.bilibili.com": "cn",
                 "www.taobao.com": "cn", "www.qq.com": "cn", "api.deepseek.com": "cn",
                 "api.openai.com": "ai", "api.anthropic.com": "ai", "openrouter.ai": "ai",
                 "cursor.com": "ai", "api2.cursor.sh": "ai", "perplexity.ai": "ai",
                 "gemini.google.com": "ai", "generativelanguage.googleapis.com": "ai",
                 "copilot.microsoft.com": "ai", "api.github.com": "proxy",
                 "github.com": "proxy", "stripe.com": "proxy", "www.apple.com": "apple",
                 "icloud.com": "apple", "parsec.app": "parsec",
                 "encryptedsni.com": "encrypted-sni", "pagead2.googlesyndication.com": "reject"}
        for host, expected in cases.items():
            with self.subTest(host=host):
                self.assertEqual(rules.explain(host, self.groups)[0], expected)

    def test_unknown_and_keyword_lookalikes_stay_proxy(self):
        for host in ["random-service.invalid", "unrelated-baidu-check.invalid",
                     "baidu.com.attacker.invalid", "openai.com.attacker.invalid",
                     "unknown-service.com.cn", "203.0.113.123", "2001:db8::123"]:
            with self.subTest(host=host):
                self.assertEqual(rules.explain(host, self.groups)[0], "final")

    def test_xiaomi_account_interconnect_and_device_services_use_cn(self):
        for host in ["account.xiaomi.com", "api.account.xiaomi.com",
                     "static.account.xiaomi.com", "cn-device.interconnect.miui.com",
                     "hyperos.mi.com", "api.io.mi.com", "miot-spec.org", "miwifi.com",
                     "mifile.cn", "mi-img.com", "mipush.com", "xiaomiwear.com", "mios.cn"]:
            with self.subTest(host=host):
                self.assertEqual(rules.explain(host, self.groups)[0], "cn")
        for host in ["xiaomi.com.attacker.invalid", "not-xiaomi.invalid", "miui.com.attacker.invalid"]:
            with self.subTest(host=host):
                self.assertEqual(rules.explain(host, self.groups)[0], "final")

    def test_wechat_public_services_and_miniprograms_use_cn(self):
        for host in ["servicewechat.com", "res.servicewechat.com", "wechat.com", "wechatpay.com",
                     "wechatlegal.net", "wechatos.net", "weixin.com", "weixinbridge.com",
                     "weixinsxy.com", "mp.weixin.qq.com", "search.wxqcloud.qq.com"]:
            with self.subTest(host=host):
                self.assertEqual(rules.explain(host, self.groups)[0], "cn")
        for host in ["servicewechat.com.attacker.invalid", "fake-wechat.invalid"]:
            with self.subTest(host=host):
                self.assertEqual(rules.explain(host, self.groups)[0], "final")

    def test_only_domain_rules_are_published(self):
        self.assertGreater(len(self.groups["cn"]), 100)
        for entries in self.groups.values():
            for kind, name in entries:
                self.assertIn(kind, rules.TYPES)
                self.assertNotEqual(name, self.policy["ignored_source_domain"])

    def test_local_rules_cannot_enable_keywords_processes_or_ips(self):
        for line in ["DOMAIN-KEYWORD,baidu", "PROCESS-NAME,curl", "GEOIP,CN",
                     "IP-ASN,4134", "IP-CIDR,0.0.0.0/0", "RULE-SET,https://example.com/a",
                     "DOMAIN-SUFFIX,com.cn", "DOMAIN,1.2.3.4", "DOMAIN,example.com,DIRECT"]:
            with self.subTest(line=line), self.assertRaises(ValueError):
                rules.parse(line, group="cn", policy=self.policy)

    def test_suffix_matches_at_label_boundary(self):
        entry = ("DOMAIN-SUFFIX", "baidu.com")
        self.assertTrue(rules.matches("news.baidu.com", entry))
        self.assertFalse(rules.matches("evilbaidu.com", entry))
        self.assertFalse(rules.matches("baidu.com.invalid", entry))

    def test_reviewed_cn_allow_precedes_adblock_without_broadening_matches(self):
        groups = {group: set(entries) for group, entries in self.groups.items()}
        groups["reject"].add(("DOMAIN-SUFFIX", "juejin.cn"))
        for host in ["juejin.cn", "api.juejin.cn"]:
            self.assertEqual(rules.explain(host, groups)[0], "cn-allow")
        for host in ["juejin.cn.attacker.invalid", "fake-juejin.cn"]:
            self.assertEqual(rules.explain(host, groups)[0], "final")
        snippet = rules.render()["surge-rules.conf"]
        active = [line for line in snippet.splitlines() if line and not line.startswith("#")]
        self.assertIn("/cn-allow.list,CN,no-resolve,", active[0])
        with self.assertRaises(ValueError):
            rules.parse("DOMAIN-SUFFIX,com.cn", group="cn-allow", policy=self.policy)

    def test_console_proxy_allow_is_exact_and_precedes_adblock(self):
        groups = {group: set(entries) for group, entries in self.groups.items()}
        console_hosts = ["analytics.google.com", "firebaseanalytics.googleapis.com",
                         "analyticsadmin.googleapis.com", "analyticsdata.googleapis.com",
                         "analyticsreporting.googleapis.com"]
        for host in console_hosts:
            groups["reject"].add(("DOMAIN-SUFFIX", host))
            self.assertEqual(rules.explain(host, groups)[0], "proxy-allow")
        groups["reject"].add(("DOMAIN-SUFFIX", "google-analytics.com"))
        self.assertEqual(rules.explain("www.google-analytics.com", groups)[0], "reject")
        self.assertEqual(rules.explain("sub.analytics.google.com", groups)[0], "reject")
        self.assertEqual(rules.explain("analytics.google.com.attacker.invalid", groups)[0], "final")
        with self.assertRaises(ValueError):
            rules.parse("DOMAIN-SUFFIX,google.com", group="proxy-allow", policy=self.policy)
        snippet = rules.render()["surge-rules.conf"]
        self.assertLess(snippet.index("/proxy-allow.list,"), snippet.index("/reject.list,"))

    def test_developer_console_data_and_seller_services_have_dedicated_policy(self):
        self.assertEqual(self.policy["policies"]["proxy-allow"], "Developer")
        cases = ["console.firebase.google.com", "firebaseanalytics.clients6.google.com",
                 "firebasecrashlytics.googleapis.com", "firestore.googleapis.com",
                 "firebasestorage.googleapis.com", "firebaseappdistribution.googleapis.com",
                 "play.google.com", "playconsole.google.com", "androidpublisher.googleapis.com",
                 "playdeveloperreporting.googleapis.com", "playconsolestatsfrontend-pa.clients6.google.com",
                 "seller.samsungapps.com", "devapi.samsungapps.com", "account.samsung.com",
                 "accounts.google.com"]
        groups = {group: set(entries) for group, entries in self.groups.items()}
        for host in cases:
            groups["reject"].add(("DOMAIN-SUFFIX", host))
            with self.subTest(host=host):
                self.assertEqual(rules.explain(host, groups)[0], "proxy-allow")
        for host in ["random.analytics.invalid", "seller.samsungapps.com.attacker.invalid"]:
            self.assertEqual(rules.explain(host, groups)[0], "final")
        self.assertEqual(rules.explain("pagead2.googlesyndication.com", groups)[0], "reject")

    def test_new_developer_domain_requires_matching_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            with (root / "rules/proxy-allow.list").open("a") as f:
                f.write("\nDOMAIN,unreviewed.example.com\n")
            with self.assertRaisesRegex(ValueError, "evidence registry differ"):
                rules.collect(root)

    def test_build_is_reproducible_and_every_remote_rule_is_no_resolve(self):
        self.assertEqual(rules.render(), rules.render())
        snippet = rules.render()["surge-rules.conf"]
        active = [x for x in snippet.splitlines() if x and not x.startswith("#")]
        self.assertEqual(active[-1], "FINAL,Proxy,dns-failed")
        self.assertTrue(all(",no-resolve," in x for x in active[:-1]))

    def test_tampered_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            (root / "vendor/sukka/domestic.conf").write_text("DOMAIN-SUFFIX,com\n")
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                rules.collect(root)

    def test_failed_upstream_update_does_not_change_pinned_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            original = (root / "sources.lock.json").read_bytes()
            with patch.object(rules, "download", side_effect=[b"DOMAIN,example.com\n", OSError("offline")]):
                with self.assertRaises(OSError):
                    rules.update(root)
            self.assertEqual((root / "sources.lock.json").read_bytes(), original)
            self.assertEqual((root / "vendor/sukka/domestic.conf").read_bytes(),
                             (ROOT / "vendor/sukka/domestic.conf").read_bytes())

    def test_successful_update_creates_report_in_fresh_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "repo"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            if (root / "docs").exists():
                shutil.rmtree(root / "docs")
            source = rules.read_json(root / "sources.lock.json")["sources"]
            payloads = [(root / item["snapshot"]).read_bytes() for item in source]
            payloads[0] += b"\nDOMAIN-SUFFIX,new-domestic.example.com\n"
            with patch.object(rules, "download", side_effect=payloads), contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(rules.update(root))
            rules.build(root, check=True)
            report = (root / "docs/UPSTREAM-UPDATE.md").read_text()
            self.assertIn("new-domestic.example.com", report)
            self.assertIn("require review", report)


if __name__ == "__main__":
    unittest.main()
