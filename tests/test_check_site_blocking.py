"""Tests for the site blocking check: parsing and verdicts, without live network."""

from __future__ import annotations

import ipaddress
import struct

import pytest

from harrix_swiss_knife.actions.site.check_site_blocking import OnCheckSiteBlocking as Check

_CF_NETWORKS = (
    ipaddress.ip_network("104.16.0.0/13"),
    ipaddress.ip_network("172.64.0.0/13"),
)


def _name(labels: list[str]) -> bytes:
    payload = b""
    for label in labels:
        raw = label.encode("ascii")
        payload += bytes((len(raw),)) + raw
    return payload + b"\x00"


def test_parse_target_adds_https_and_default_port() -> None:
    target = Check._parse_target("harrix.dev")
    assert target.host == "harrix.dev"
    assert target.port == 443
    assert target.scheme == "https"
    assert target.url == "https://harrix.dev/"


def test_parse_target_rejects_blank_and_non_http() -> None:
    with pytest.raises(ValueError, match="site address"):
        Check._parse_target("   ")
    with pytest.raises(ValueError, match="http"):
        Check._parse_target("ftp://harrix.dev/")


def test_hosts_override_ignores_comments() -> None:
    text = "# harrix.dev\n127.0.0.1 example.com harrix.dev\n"
    assert Check._hosts_override(text, "harrix.dev") == "127.0.0.1"
    assert Check._hosts_override(text, "other.dev") is None


def test_dns_mismatch_ignores_different_cloudflare_edges() -> None:
    assert not Check._dns_mismatch(("104.21.1.1",), ("172.67.2.2",), _CF_NETWORKS)


def test_dns_mismatch_when_system_resolver_is_empty() -> None:
    assert Check._dns_mismatch((), ("93.184.216.34",), _CF_NETWORKS)


def test_dns_mismatch_when_addresses_differ() -> None:
    assert Check._dns_mismatch(("8.8.8.8",), ("93.184.216.34",), _CF_NETWORKS)


def test_parse_dns_message_reads_compressed_a_and_ns() -> None:
    question = _name(["example", "com"]) + struct.pack("!HH", 1, 1)
    header = struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 1, 0)
    answer = b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 60, 4) + bytes((93, 184, 216, 34))
    ns_rdata = _name(["a", "iana-servers", "net"])
    authority = b"\xc0\x0c" + struct.pack("!HHIH", 2, 1, 60, len(ns_rdata)) + ns_rdata
    rcode, ips, nameservers = Check._parse_dns_message(header + question + answer + authority)
    assert rcode == "NOERROR"
    assert ips == ("93.184.216.34",)
    assert nameservers == ("a.iana-servers.net",)


def test_parse_tracert_windows_and_russian_timeout() -> None:
    timeout = (
        "\u041f\u0440\u0435\u0432\u044b\u0448\u0435\u043d \u0438\u043d\u0442\u0435\u0440\u0432\u0430\u043b "
        "\u043e\u0436\u0438\u0434\u0430\u043d\u0438\u044f \u0434\u043b\u044f "
        "\u0437\u0430\u043f\u0440\u043e\u0441\u0430."
    )
    text = f"""
Tracing route to 104.21.1.1
  1    <1 ms    <1 ms    <1 ms  192.168.1.1
  2     *        *        *     {timeout}
  3    10 ms    11 ms    12 ms  10.20.30.1
"""
    hops = Check._parse_tracert(text)
    assert [(hop.index, hop.ip) for hop in hops] == [
        (1, "192.168.1.1"),
        (2, None),
        (3, "10.20.30.1"),
    ]


def test_extract_cf_error_codes_and_challenge() -> None:
    assert Check._extract_cf_error("Error code: 1020") == "1020"
    assert Check._extract_cf_error("<title>Just a moment...</title>") == "challenge"
    blocked = "\u0441\u0430\u0439\u0442 \u0437\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d"
    assert Check._extract_cf_error(blocked) == "blockpage"
    assert Check._extract_cf_error("hello") is None


def test_classify_hosts_file() -> None:
    verdict, title, _summary = Check._classify(Check.BlockingFacts(hosts_override="127.0.0.1"))
    assert verdict == "hosts"
    assert title == "This computer"


def test_classify_dns_when_public_address_still_opens() -> None:
    facts = Check.BlockingFacts(
        dns_mismatch=True,
        connects=(Check.ConnectProbe(ip="104.21.1.1", tcp_ok=True, tls_ok=True, http_status=200),),
    )
    verdict, title, summary = Check._classify(facts)
    assert verdict == "dns"
    assert title == "DNS"
    assert "public" in summary


def test_classify_router_when_trace_dies_on_gateway() -> None:
    facts = Check.BlockingFacts(
        connects=(Check.ConnectProbe(ip="104.21.1.1", on_cloudflare=True, tcp_error="timeout"),),
        hops=(Check.TraceHop(1, "192.168.1.1"), Check.TraceHop(2, None), Check.TraceHop(3, None)),
        trace_ran=True,
        control_dns_ok=True,
        control_tcp_ok=True,
    )
    verdict, title, _summary = Check._classify(facts)
    assert verdict == "router"
    assert title == "Router"


def test_classify_sni_filter() -> None:
    facts = Check.BlockingFacts(
        connects=(
            Check.ConnectProbe(
                ip="104.21.1.1",
                tcp_ok=True,
                tls_ok=False,
                tls_error="reset",
                decoy_tls_ok=True,
            ),
        ),
    )
    assert Check._classify(facts)[0] == "sni"


def test_classify_cloudflare_origin_and_policy() -> None:
    origin = Check.BlockingFacts(
        connects=(
            Check.ConnectProbe(
                ip="104.21.1.1",
                on_cloudflare=True,
                tcp_ok=True,
                tls_ok=True,
                http_status=522,
                cf_error="522",
                cf_ray=True,
            ),
        ),
    )
    policy = Check.BlockingFacts(
        connects=(
            Check.ConnectProbe(
                ip="104.21.1.1",
                on_cloudflare=True,
                tcp_ok=True,
                tls_ok=True,
                http_status=403,
                cf_error="1020",
                cf_ray=True,
            ),
        ),
    )
    assert Check._classify(origin)[0] == "origin"
    assert Check._classify(policy)[0] == "cloudflare"


def test_classify_reachable_and_nxdomain() -> None:
    reachable = Check.BlockingFacts(
        connects=(
            Check.ConnectProbe(
                ip="104.21.1.1",
                on_cloudflare=True,
                tcp_ok=True,
                tls_ok=True,
                http_status=200,
            ),
        ),
    )
    missing = Check.BlockingFacts(
        lookups=(
            Check.DnsLookup("System", (), (), "NXDOMAIN", ""),
            Check.DnsLookup("8.8.8.8", (), (), "NXDOMAIN", ""),
        ),
        control_dns_ok=True,
        control_tcp_ok=True,
    )
    assert Check._classify(reachable)[0] == "reachable"
    assert Check._classify(missing)[0] == "nxdomain"


def test_format_report_names_the_level() -> None:
    facts = Check.BlockingFacts(hosts_override="127.0.0.1")
    report = Check._format_report(facts, Check._classify(facts))
    assert "Level: This computer" in report
    assert "127.0.0.1" in report
