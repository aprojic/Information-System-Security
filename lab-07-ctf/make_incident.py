"""Lab 07 — generates YOUR incident.log from your student ID.

    ISS_SECRET='<from the instructor>' python3 make_incident.py <student-id>

The flag hidden in the log (Base64 in the export request) is derived from your
student ID, so it is unique. After generating it, analyse `incident.log` as the
lab describes.
"""
import base64
import hashlib
import hmac
import os
import sys

if len(sys.argv) != 2:
    sys.exit("usage: ISS_SECRET=... python3 make_incident.py <student-id>")
MB = sys.argv[1]
SECRET = os.environ.get("ISS_SECRET")
if not SECRET:
    sys.exit("error: set ISS_SECRET (from the instructor)")

hex6 = hmac.new(SECRET.encode(), f"lab07:{MB}".encode(), hashlib.sha256).hexdigest()[:6]
flag = f"ASPIRA{{sis_incident_{hex6}}}"
b64 = base64.b64encode(flag.encode()).decode()

ATK = "203.0.113.77"
lines = [
    f'10.0.0.23 - - [14/Oct/2026:09:12:03 +0200] "GET /products HTTP/1.1" 200 5312 "-" "Mozilla/5.0"',
    f'10.0.0.51 - - [14/Oct/2026:09:12:40 +0200] "GET /products/42 HTTP/1.1" 200 1840 "-" "Mozilla/5.0"',
    f'10.0.0.23 - - [14/Oct/2026:09:13:09 +0200] "GET /cart HTTP/1.1" 200 980 "-" "Mozilla/5.0"',
]
for i, p in enumerate(["/admin", "/backup", "/.git/config", "/phpmyadmin",
                       "/wp-login.php", "/.env", "/server-status", "/api/v1/config"]):
    lines.append(f'{ATK} - - [14/Oct/2026:10:02:{i*7%60:02d} +0200] "GET {p} HTTP/1.1" 404 199 "-" "curl/8.5.0"')
lines += [
    f'{ATK} - - [14/Oct/2026:10:03:11 +0200] "GET /login HTTP/1.1" 200 1420 "-" "curl/8.5.0"',
    f'{ATK} - - [14/Oct/2026:10:05:02 +0200] "GET /search?q=%27%20OR%20%271%27%3D%271 HTTP/1.1" 500 612 "-" "curl/8.5.0"',
    f'{ATK} - - [14/Oct/2026:10:05:44 +0200] "GET /search?q=%27%20UNION%20SELECT%20username,password%20FROM%20users-- HTTP/1.1" 200 8710 "-" "curl/8.5.0"',
    f'{ATK} - - [14/Oct/2026:10:06:20 +0200] "POST /login HTTP/1.1" 401 180 "-" "curl/8.5.0"',
    f'{ATK} - - [14/Oct/2026:10:06:33 +0200] "POST /login HTTP/1.1" 302 0 "-" "curl/8.5.0"',
    f'10.0.0.51 - - [14/Oct/2026:10:07:00 +0200] "GET /products HTTP/1.1" 200 5312 "-" "Mozilla/5.0"',
    f'{ATK} - - [14/Oct/2026:10:08:15 +0200] "GET /export?data={b64} HTTP/1.1" 200 44102 "-" "curl/8.5.0"',
    f'{ATK} - - [14/Oct/2026:10:09:02 +0200] "GET /logout HTTP/1.1" 302 0 "-" "curl/8.5.0"',
    f'10.0.0.23 - - [14/Oct/2026:10:15:00 +0200] "GET /products HTTP/1.1" 200 5312 "-" "Mozilla/5.0"',
]

with open("incident.log", "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"OK: incident.log written ({len(lines)} lines). Analyse it as the lab describes.")
