# Dragonfly-Eye APT v3.0

A next-generation, context-aware, non-interactive intelligence framework designed for high-value target tracking and covert geolocation reconnaissance.

## Description

**Dragonfly-Eye** is an advanced passive reconnaissance engine engineered to execute zero-prompt geolocation and infrastructure mapping against hardened targets. Inspired by the compound vision and unmatched hunting efficiency of the dragonfly, this framework shifts away from traditional, noisy active tracking mechanisms (such as OS-level GPS permission dialogs) that immediately alert sophisticated targets.

Instead, the engine utilizes a **360-Degree Passive Compound Vision** methodology. By executing asynchronous, non-interactive telemetry extraction at the browser runtime level, it consolidates multiple covert data vector lenses simultaneously:
* **Transport-Layer VPN/Proxy Evasion:** Leverages sub-200ms WebRTC STUN queries to force local interface leaks, bypassing active commercial VPNs and routing proxies to reveal the target's true origin ISP address.
* **Hardware & Environment Fingerprinting:** Extracts granular hardware profiles (CPU architecture, custom rendering canvas, core density) paired with precision battery state indicators to determine the target's operational state (stationary vs. in-transit).
* **Passive Infrastructure Triangulation:** Cross-references true origin network routing, hardware timezone skew, and localized telemetry to isolate target geolocation boundaries on a global scale.

The entire operation executes silently within **150 milliseconds** of initial interaction before gracefully redirecting the target to a legitimate media proxy, achieving a zero-trace operational footprint on the client side.

---

## Deployment Guide

### Prerequisites
The C2 listening node requires a Python 3.x environment and must be deployed on an infrastructure with a publicly routable IP address (or utilizing an edge-tunneling mechanism like `ngrok` for localized testing).

### Installation

1. Clone the repository to your operational environment:
```bash
cd dragonfly-eye-apt
