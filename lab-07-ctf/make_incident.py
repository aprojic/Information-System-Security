"""Lab 07 — generates YOUR incident.log from your student ID.

    ISS_SECRET='<from the instructor>' python3 make_incident.py <student-id>

The log is one day of a web shop's access log: ordinary visitors, a monitoring
service, a search-engine crawler, a scanner that finds nothing, and one attacker
who gets in. The attacker's address, the number of login attempts, the times and
the flag hidden in the exfiltration request are derived from your student ID,
so every student's log is different. The same ID and secret always give the
same file, byte for byte.
"""
import base64
import hashlib
import hmac
import os
import sys

DATE, ZONE = "14/Oct/2026", "+0200"
DAY_START, DAY_END = 6 * 3600, 14 * 3600          # the log covers 06:00-14:00

BROWSERS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
]
CRAWLER_AGENT = "ExampleBot/2.1 (+http://crawler.example/bot.html)"
ATTACK_TOOLS = ["curl/8.5.0", "python-requests/2.32.3", "Go-http-client/1.1"]
WORDS = ["juice", "apple", "orange", "lemon", "banana", "gift", "sale", "melon", "smoothie", "bottle"]
PROBES = [  # what scanners and the attacker look for; none of it exists on this server
    "/admin.php", "/backup", "/backup.zip", "/.git/config", "/phpmyadmin", "/wp-login.php", "/.env",
    "/server-status", "/api/v1/config", "/config.php", "/db.sql", "/old", "/test", "/.aws/credentials",
    "/wp-admin", "/xmlrpc.php", "/.svn/entries", "/dump.sql", "/console", "/actuator/health", "/debug",
    "/shell.php", "/id_rsa", "/.htaccess", "/cgi-bin/test.cgi", "/vendor/phpunit", "/api/swagger.json",
    "/login.bak", "/site.tar.gz", "/users.csv", "/private", "/tmp", "/setup.php", "/install.php",
    "/manager/html", "/solr", "/jenkins", "/.DS_Store", "/web.config", "/secret.txt", "/api/keys",
    "/staging", "/portal", "/owa", "/remote/login", "/boaform/admin", "/HNAP1", "/cgi-bin/luci",
]
FORBIDDEN = {"/server-status", "/.htaccess", "/private", "/manager/html"}   # answered 403 instead of 404
SQLI = [  # URL-encoded, as it appears in a real access log (%27 is a single quote)
    "/search?q=%27",
    "/search?q=%27%20OR%20%271%27%3D%271",
    "/search?q=%27%20OR%201%3D1--",
    "/search?q=%27%20ORDER%20BY%203--",
    "/search?q=%27%20UNION%20SELECT%20NULL,NULL--",
]
SQLI_HIT = "/search?q=%27%20UNION%20SELECT%20username,password%20FROM%20users--"


class Stream:
    """Deterministic numbers from the secret and the student ID (no `random`, so
    the output does not depend on the Python version or the machine)."""

    def __init__(self, secret, mb):
        self.key = hmac.new(secret.encode(), f"lab07-log:{mb}".encode(), hashlib.sha256).digest()
        self.n = 0

    def below(self, k):
        self.n += 1
        block = hashlib.sha256(self.key + self.n.to_bytes(8, "big")).digest()
        return int.from_bytes(block[:8], "big") % k

    def pick(self, seq):
        return seq[self.below(len(seq))]

    def take(self, seq, k):
        pool, out = list(seq), []
        for _ in range(k):
            out.append(pool.pop(self.below(len(pool))))
        return out


def make_flag(mb, secret):
    hex6 = hmac.new(secret.encode(), f"lab07:{mb}".encode(), hashlib.sha256).hexdigest()[:6]
    return f"ASPIRA{{sis_incident_{hex6}}}"


def clock(sec):
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def build(mb, secret):
    """Returns (lines, answers) for one student."""
    r = Stream(secret, mb)
    events = []

    def add(ip, sec, method, path, status, size, agent):
        text = f'{ip} - - [{DATE}:{clock(sec)} {ZONE}] "{method} {path} HTTP/1.1" {status} {size} "-" "{agent}"'
        events.append((sec, len(events), text))

    # Addresses: staff on the internal network, everyone else from the documentation ranges.
    staff = [f"10.0.0.{o}" for o in r.take(range(20, 200), 12)]
    net1 = r.take(range(2, 250), 16)
    net2 = r.take(range(2, 250), 14)
    net3 = r.take(range(2, 250), 7)
    customers = ([f"192.0.2.{o}" for o in net1[:15]] + [f"198.51.100.{o}" for o in net2[:13]]
                 + [f"203.0.113.{o}" for o in net3[:6]])
    scanner, crawler = f"192.0.2.{net1[15]}", f"198.51.100.{net2[13]}"
    attacker, monitor = f"203.0.113.{net3[6]}", "10.0.0.5"

    # 1. Ordinary visitors.
    next_param = base64.b64encode(b"/account").decode()
    for ip in staff + customers:
        agent, is_staff = r.pick(BROWSERS), ip.startswith("10.")
        for _ in range(40 + r.below(60)):
            sec, x = DAY_START + r.below(DAY_END - DAY_START), r.below(100)
            if x < 14:
                add(ip, sec, "GET", "/", 200, 4100 + r.below(300), agent)
            elif x < 30:
                add(ip, sec, "GET", "/products", 200, 5200 + r.below(400), agent)
            elif x < 55:
                add(ip, sec, "GET", f"/products/{1 + r.below(60)}", 200, 1700 + r.below(500), agent)
            elif x < 63:
                add(ip, sec, "GET", "/search?q=" + r.pick(WORDS), 200, 2100 + r.below(900), agent)
            elif x < 71:
                add(ip, sec, "GET", "/cart", 200, 900 + r.below(200), agent)
            elif x < 78:
                add(ip, sec, "GET", "/static/app.js", *r.pick([(200, 48213), (304, 0), (304, 0)]), agent)
            elif x < 83:
                add(ip, sec, "GET", "/static/style.css", *r.pick([(200, 9120), (304, 0), (304, 0)]), agent)
            elif x < 87:
                add(ip, sec, "GET", "/login?next=" + next_param, 200, 1420, agent)
            elif x < 91:
                add(ip, sec, "POST", "/login", 302, 0, agent)
            elif x < 92:
                add(ip, sec, "POST", "/login", 401, 180, agent)        # a mistyped password
            elif x < 95:
                add(ip, sec, "GET", "/account", 200, 2300 + r.below(400), agent)
            elif x < 97 and is_staff:
                add(ip, sec, "GET", "/export?format=csv", 200, 5000 + r.below(9000), agent)
            elif x < 98:
                add(ip, sec, "GET", "/favicon.ico", 404, 199, agent)
            else:
                add(ip, sec, "GET", "/logout", 302, 0, agent)

    # 2. Monitoring: one health check a minute, all day. The busiest address, and harmless.
    for sec in range(DAY_START + r.below(60), DAY_END, 60):
        add(monitor, sec, "GET", "/health", 200, 17, "UptimeCheck/1.0")

    # 3. A search-engine crawler walking the product pages.
    sec = DAY_START + 600 + r.below(1200)
    add(crawler, sec, "GET", "/robots.txt", 200, 68, CRAWLER_AGENT)
    for _ in range(240 + r.below(80)):
        sec += 20 + r.below(60)
        add(crawler, sec, "GET", f"/products/{1 + r.below(60)}", 200, 1700 + r.below(500), CRAWLER_AGENT)

    # 4. A scanner that tries every door and finds none open: nothing but 404 and 403.
    sec = DAY_START + 300 + r.below(2 * 3600)
    for _ in range(70 + r.below(40)):
        sec += 1 + r.below(3)
        path = r.pick(PROBES)
        add(scanner, sec, "GET", path, 403 if path in FORBIDDEN else 404, 199, "Mozilla/5.0 zgrab/0.x")

    # 5. The attacker: reconnaissance, injection, password guessing, access, exfiltration.
    tool = r.pick(ATTACK_TOOLS)
    sec = first_seen = 9 * 3600 + r.below(3 * 3600)
    add(attacker, sec, "GET", "/robots.txt", 200, 68, tool)
    for path in r.take(PROBES, 18 + r.below(13)):
        sec += 3 + r.below(7)
        add(attacker, sec, "GET", path, 403 if path in FORBIDDEN else 404, 199, tool)
    sec += 3 + r.below(7)
    add(attacker, sec, "GET", "/login", 200, 1420, tool)
    sec += 60 + r.below(180)
    for path in r.take(SQLI, 2 + r.below(4)):
        sec += 8 + r.below(30)
        add(attacker, sec, "GET", path, 500, 612, tool)
    sec += 8 + r.below(30)
    add(attacker, sec, "GET", SQLI_HIT, 200, 8000 + r.below(1500), tool)
    sec += 30 + r.below(90)
    failed = 6 + r.below(13)
    for _ in range(failed):
        sec += 1 + r.below(3)
        add(attacker, sec, "POST", "/login", 401, 180, tool)
    sec += 1 + r.below(3)
    login_time = sec
    add(attacker, sec, "POST", "/login", 302, 0, tool)
    for path, size in (("/account", 2300), ("/admin", 3100), ("/admin/users", 6400 + r.below(1000))):
        sec += 5 + r.below(20)
        add(attacker, sec, "GET", path, 200, size, tool)
    sec += 10 + r.below(40)
    exfil_time, flag = sec, make_flag(mb, secret)
    add(attacker, sec, "GET", "/export?data=" + base64.b64encode(flag.encode()).decode(), 200,
        40000 + r.below(20000), tool)
    sec += 5 + r.below(30)
    add(attacker, sec, "GET", "/logout", 302, 0, tool)

    lines = [text for _, _, text in sorted(events)]
    answers = {"attacker_ip": attacker, "failed_logins": failed, "first_seen": clock(first_seen),
               "login_time": clock(login_time), "exfil_time": clock(exfil_time), "flag": flag}
    return lines, answers


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: ISS_SECRET=... python3 make_incident.py <student-id>")
    secret = os.environ.get("ISS_SECRET")
    if not secret:
        sys.exit("error: set ISS_SECRET (from the instructor)")
    lines, _ = build(sys.argv[1], secret)
    with open("incident.log", "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"OK: incident.log written ({len(lines)} lines). Analyse it as the lab describes.")


if __name__ == "__main__":
    main()
