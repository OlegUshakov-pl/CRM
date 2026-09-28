"""Guards for fetching external URLs.

Protects against SSRF (internal/metadata addresses) and local file reads
(``file://`` and friends) whenever the application fetches a URL that is
directly or indirectly controlled by a user.

Known limitation: DNS rebinding between validation and the actual connect
cannot be fully prevented with urllib (the resolver runs twice). Schemes and
every redirect hop are validated, which closes the practical vectors.
"""
import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request

ALLOWED_SCHEMES = ('http', 'https')
DEFAULT_MAX_BYTES = 10 * 1024 * 1024  # 10 MB


class UnsafeURLError(ValueError):
    """Raised when a URL must not be fetched."""


def _parse(url):
    url = (url or '').strip()
    if not url:
        raise UnsafeURLError('Please provide a URL.')
    try:
        parts = urllib.parse.urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise UnsafeURLError('Invalid URL.') from exc
    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        raise UnsafeURLError('Only public http and https URLs are allowed.')
    host = parts.hostname
    if not host:
        raise UnsafeURLError('URL has no host.')
    if port is None:
        port = 443 if parts.scheme.lower() == 'https' else 80
    return url, host, port


def _resolved_ips(host, port):
    """Resolve host to a set of ipaddress objects. Empty set = failure."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError, ValueError, OSError):
        return set()
    ips = set()
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        mapped = getattr(ip, 'ipv4_mapped', None)
        if mapped is not None:
            ip = ipaddress.ip_address(mapped)
        ips.add(ip)
    return ips


def validate_public_url(url):
    """Allow only http(s) URLs whose host resolves exclusively to public IPs."""
    url, host, port = _parse(url)
    ips = _resolved_ips(host, port)
    if not ips:
        raise UnsafeURLError('Could not resolve the host of this URL.')
    for ip in ips:
        if not ip.is_global:
            raise UnsafeURLError(
                'Access to private or internal network addresses is not allowed.'
            )
    return url


def validate_service_url(url):
    """Allow http(s) to local/private services (e.g. Ollama on localhost).

    Blocks link-local addresses (cloud metadata), multicast and unspecified
    addresses, but keeps loopback and private ranges reachable because local
    integrations depend on them.
    """
    url, host, port = _parse(url)
    ips = _resolved_ips(host, port)
    if not ips:
        raise UnsafeURLError('Could not resolve the host of this URL.')
    for ip in ips:
        if ip.is_link_local or ip.is_multicast or ip.is_unspecified:
            raise UnsafeURLError('This address range is not allowed.')
    return url


class _ValidatingRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Re-validate scheme and host of every redirect target before following."""

    def __init__(self, validator):
        self._validator = validator

    def redirect_request(self, req, fp, code, msg, headers, newurl, *args, **kwargs):
        try:
            self._validator(newurl)
        except UnsafeURLError as exc:
            raise urllib.error.HTTPError(
                req.full_url, code, f'Redirect blocked: {exc}', headers, fp
            ) from exc
        return super().redirect_request(req, fp, code, msg, headers, newurl, *args, **kwargs)


def build_safe_opener(validator=validate_public_url, ssl_context=None):
    """Opener whose redirects are re-validated (no file:// or internal hops)."""
    handlers = [_ValidatingRedirectHandler(validator)]
    if ssl_context is not None:
        handlers.append(urllib.request.HTTPSHandler(context=ssl_context))
    return urllib.request.build_opener(*handlers)


def safe_open(req, *, timeout=15, validator=validate_public_url, ssl_context=None):
    """Open *req* with redirect validation. Returns the response object."""
    return build_safe_opener(validator, ssl_context).open(req, timeout=timeout)


def safe_urlopen(req, *, timeout=15, max_bytes=DEFAULT_MAX_BYTES,
                 validator=validate_public_url, ssl_context=None):
    """Fetch *req* with redirect validation and a response size limit.

    Returns the response body as bytes.
    """
    with safe_open(req, timeout=timeout, validator=validator, ssl_context=ssl_context) as response:
        if max_bytes is None:
            return response.read()
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise UnsafeURLError('Response is too large to import.')
        return data
