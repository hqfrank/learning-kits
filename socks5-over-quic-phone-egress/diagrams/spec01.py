# -*- coding: utf-8 -*-
# 01 — Two paths, both dialled by the phone (notes A1, B3).
from _common import *

T = Tags()
W = 1280
PAGE = dict(name="01-two-paths", w=W, h=0)

sp = V("socks_listen_port_illustrative"); t_sp = T("socks_listen_port_illustrative")
qp = V("quic_listen_port_illustrative"); t_qp = T("quic_listen_port_illustrative")
fr = V("front_door_port_range_illustrative"); t_fr = T("front_door_port_range_illustrative")
cap = V("phone_max_incoming_streams_illustrative"); t_cap = T("phone_max_incoming_streams_illustrative")
ka = V("keepalive_illustrative"); t_ka = T("keepalive_illustrative")
nat = V("udp_nat_idle_assumption"); t_nat = T("udp_nat_idle_assumption")
md = V("metadata_address"); t_md = T("metadata_address")
ports = V("allowed_ports_illustrative"); t_ports = T("allowed_ports_illustrative")
doc = V("documentation_addresses", "ipv4")[2]; t_doc = T("documentation_addresses")

BOXES = [title("Two paths, both dialled by the phone: HTTPS tells it where the tunnel is and which certificate to trust; "
               "QUIC carries one stream per tool TCP connection, and the site sees the phone's address", W, h=44)]

# frames (fill none so edges stay visible)
BOXES += [
    frame("f_cloud", 30, 70, 560, 420, "CLOUD SIDE: the agent instance sits in a private subnet", CLOUD),
    frame("f_mid", 610, 70, 220, 420, "PUBLIC EDGE", EDGE),
    frame("f_phone", 850, 70, 240, 420, "USER'S NETWORK", PHONE),
]
BOXES += [
    box("tool", 50, 110, 250, 90,
        "AGENT TOOL (curl, an HTTP library)\nreads ALL_PROXY = socks5h://localhost:%s %s\nset once at boot; speaks SOCKS5 to the listener; no tool code changes" % (sp, t_sp),
        CLOUD, font=11),
    box("noproxy", 50, 240, 250, 100,
        "NO_PROXY list: localhost, the metadata address %s %s, internal suffixes, the model API and cloud APIs\n-> these never go through the phone" % (md, t_md),
        NOTE, font=10.5, align="left"),
    box("listener", 330, 110, 240, 100,
        "PASSTHROUGH LISTENER\nlocalhost:%s %s, always up\nreads CONNECT only for a deny list, then forwards the SOCKS5 bytes unchanged" % (sp, t_sp),
        CLOUD, font=11),
    box("quic", 330, 262, 240, 100,
        "QUIC SERVER  UDP :%s %s\nprivate ALPN socks5-over-quic\nself-signed certificate made at boot\nopens 1 stream per tool connection" % (qp, t_qp),
        CLOUD, font=11),
    box("api", 330, 385, 240, 85,
        "ASSISTANT SERVICE API\nexisting HTTPS chat API, user login\nconfig endpoint: host, port, fingerprint, ALPN, single-use token",
        CTRL, font=10.5),
    box("direct", 630, 105, 180, 115,
        "SITE REACHED DIRECT\nfrom the cloud address (no phone connected, or a NO_PROXY match): sees a data-centre IP",
        SITE, font=10.5, dashed=True),
    box("fd", 630, 257, 170, 120,
        "ANYCAST UDP FRONT DOOR\nstatic public %s.x %s; one public port per instance from %s %s; deny-by-default; does NOT filter sources"
        % (".".join(doc.split(".")[:3]), t_doc, "-".join(map(str, fr)), t_fr),
        EDGE, font=10.5),
    box("htp", 630, 385, 180, 85,
        "HTTPS TUNNEL PROVIDER for the control channel (TCP only: cannot carry the UDP data path)",
        CTRL, font=10.5),
    box("nat", 870, 105, 200, 115,
        "HOME OR CARRIER NAT\nsees only an outbound UDP flow; no port forwarding. Keepalive every %s s %s stays under the %s s NAT assumption %s"
        % (ka, t_ka, nat, t_nat),
        NOTE, font=10.5),
    box("phone", 885, 257, 190, 213,
        "PHONE APP (in the foreground, during a chat)\n\n1  calls the config endpoint over HTTPS\n2  dials QUIC, checks the pinned fingerprint and ALPN\n3  SOCKS5 server: resolves the name with its own resolver\n4  destination filter: no private ranges; ports %s %s only\n5  opens TCP from the phone's address"
        % ("/".join(map(str, ports)), t_ports),
        PHONE, font=10.5, align="left", valign="top"),
    box("site", 1110, 105, 150, 155,
        "WEB SITE\nsees the PHONE's address; the DNS answer was picked for the phone's location (socks5h)",
        SITE, font=11),
]

EDGES = [
    dict(src="tool", dst="listener", sx=1, sy=0.4, dx=0, dy=0.4, color=DATA_C, bold=True),
    dict(src="listener", dst="quic", sx=0.5, sy=1, dx=0.5, dy=0, color=DATA_C, bold=True,
         label="1 new QUIC stream per tool TCP connection (cap %s %s)" % (cap, t_cap),
         lpos=(450, 236), lw=330),
    dict(src="phone", dst="fd", sx=0, sy=0.25, dx=1, dy=0.5, color=DATA_C, bold=True,
         label="QUIC/UDP\nphone\ndials", lpos=(842, 355), lw=70),
    dict(src="fd", dst="quic", sx=0, sy=0.5, dx=1, dy=0.5, color=DATA_C, bold=True,
         label="port map ->\nprivate :%s" % qp, lpos=(600, 345), lw=70),
    dict(src="phone", dst="htp", sx=0, sy=0.85, dx=1, dy=0.5, color=CTRL_C,
         label="HTTPS", lpos=(842, 455), lw=50),
    dict(src="htp", dst="api", sx=0, sy=0.5, dx=1, dy=0.5, color=CTRL_C),
    dict(src="phone", dst="site", sx=1, sy=0.2, dx=0.5, dy=1, color=DATA_C, bold=True,
         points=[(1185, 290)], label="TCP from the\nphone's address", lpos=(1185, 330), lw=110),
    dict(src="listener", dst="direct", sx=1, sy=0.25, dx=0, dy=0.3, color=DIR_C, dashed=True,
         label="direct fallback", lpos=(600, 120), lw=60),
]

BOXES.append(box("legend", 30, 507, 1230, 44,
                 "Legend:  green bold arrows = the data path (QUIC over UDP, then TCP from the phone)  |  purple = the control channel (HTTPS over TCP, the app's existing login)  |  "
                 "grey dashed = direct connection from the cloud address  |  blue = cloud instance  |  amber = public edge  |  green boxes = user's network.  "
                 "The two paths share no state. Arrows point the way each connection is dialled.",
                 WHITE, align="left", font=11))

src_box, bottom = footer_box(T, [
    "Mechanism: notes/A1-the-end-to-end-picture.md (two paths, one request, static environment, NO_PROXY, direct fallback); notes/B3-who-dials-whom.md "
    "(phone dials out, cloud opens streams, port map, no source filter, NAT keepalive); B4 (pin, ALPN); B5 (config call, token); C1 (phone destination filter). "
    "Front-door address: only the first three octets of a documentation range are shown."],
    30, 562, 1230)
BOXES.append(src_box)
PAGE["h"] = bottom + 16
