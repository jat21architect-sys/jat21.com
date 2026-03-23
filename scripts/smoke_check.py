"""HTTP smoke check for a running Architecture Portfolio deployment.

Checks status codes, key page content, and post-deploy specifics
(branded 404, admin reachability).

Usage:
    python scripts/smoke_check.py --base-url https://your-domain.com

Exit code 0 = all checks passed.
Exit code 1 = one or more checks failed.
"""
import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request

ROUTES = [
    ("/", "home"),
    ("/about/", "about"),
    ("/services/", "services"),
    ("/contact/", "contact"),
    ("/projects/", "projects list"),
    ("/sitemap.xml", "sitemap"),
    ("/robots.txt", "robots"),
    ("/static/images/favicon.svg", "favicon asset"),
]


def fetch(url: str, timeout: float) -> tuple[int, bytes]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "architecture-portfolio-smoke/1.0.0"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.getcode(), response.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL to smoke-check, e.g. http://127.0.0.1:8000 or https://example.com",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Per-request timeout in seconds.",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    failures: list[str] = []
    responses: dict[str, bytes] = {}

    for path, name in ROUTES:
        url = urllib.parse.urljoin(base_url + "/", path.lstrip("/"))
        try:
            status_code, body = fetch(url, timeout=args.timeout)
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            body = exc.read()
        except Exception as exc:  # noqa: BLE001 - smoke script should report any runtime failure
            print(f"FAIL error {name}: {exc}")
            failures.append(f"{name} request failed: {exc}")
            continue

        responses[path] = body
        ok = status_code == 200
        sym = "OK  " if ok else "FAIL"
        print(f"{sym} {status_code} {name}")
        if not ok:
            failures.append(f"{name} returned {status_code}")

    content_checks = [
        ("/", b"favicon.svg", "home contains favicon link"),
        ("/", b"skip-link", "home contains skip-link"),
        ("/sitemap.xml", b"urlset", "sitemap contains urlset"),
        ("/robots.txt", b"Sitemap:", "robots advertises sitemap"),
    ]
    for path, needle, label in content_checks:
        body = responses.get(path, b"")
        found = needle in body
        sym = "OK  " if found else "MISS"
        print(f"{sym} {label}")
        if not found:
            failures.append(label)

    # ------------------------------------------------------------------
    # Post-deploy checks: branded 404 and admin reachability
    # ------------------------------------------------------------------
    print()
    print("Post-deploy checks:")

    # Branded 404 — confirm custom template is served, not Django's default
    _404_url = base_url + "/smoke-check-deliberate-404-xyz-9q7r/"
    try:
        _status, _body = fetch(_404_url, timeout=args.timeout)
    except urllib.error.HTTPError as exc:
        _status, _body = exc.code, exc.read()
    except Exception as exc:  # noqa: BLE001
        _status, _body = 0, b""
        print(f"FAIL error branded 404: {exc}")
        failures.append(f"branded 404 request failed: {exc}")
    if _status != 0:
        branded = _status == 404 and b"Page not found" in _body and b"Back to home" in _body
        sym = "OK  " if branded else "FAIL"
        print(f"{sym} {_status} branded 404 template")
        if not branded:
            failures.append(f"branded 404 check failed (status={_status}, template={'OK' if b'Page not found' in _body else 'MISSING'})")

    # Admin reachable — expect 200 (login page) or 302 (redirect to login)
    _admin_url = base_url + "/admin/login/"
    try:
        _status, _ = fetch(_admin_url, timeout=args.timeout)
    except urllib.error.HTTPError as exc:
        _status = exc.code
    except Exception as exc:  # noqa: BLE001
        _status = 0
        print(f"FAIL error admin reachability: {exc}")
        failures.append(f"admin reachability failed: {exc}")
    if _status != 0:
        admin_ok = _status in (200, 302)
        sym = "OK  " if admin_ok else "FAIL"
        print(f"{sym} {_status} admin login page reachable")
        if not admin_ok:
            failures.append(f"admin login page returned {_status}")

    print()
    if failures:
        print(f"FAILED: {len(failures)} checks")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
