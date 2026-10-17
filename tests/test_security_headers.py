"""ทุกคำตอบต้องมี security headers — CSP กันสคริปต์/การส่งข้อมูลออกไปเว็บอื่น · HSTS บังคับ HTTPS"""


def test_every_response_has_security_headers(client):
    for path in ("/", "/health", "/api/galaxy/nodes", "/static/king_diadem_universe.html"):
        h = client.get(path).headers
        csp = h.get("content-security-policy", "")
        assert "default-src 'self'" in csp and "connect-src 'self'" in csp and "frame-ancestors 'none'" in csp, path
        assert "object-src 'none'" in csp and "base-uri 'self'" in csp
        assert h.get("strict-transport-security", "").startswith("max-age=31536000")
        assert "camera=()" in h.get("permissions-policy", "")
        assert h.get("x-frame-options") == "DENY" and h.get("x-content-type-options") == "nosniff"


def test_starlette_is_not_a_known_vulnerable_version():
    """starlette 0.37.2 (มากับ fastapi 0.111) มีช่องโหว่ที่รู้แล้ว — ต้องเป็น 1.3.1 ขึ้นไป"""
    import starlette
    major, minor, patch = (int(x) for x in starlette.__version__.split(".")[:3])
    assert (major, minor, patch) >= (1, 3, 1), starlette.__version__
