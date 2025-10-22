import json
import re
import urllib.request
from typing import Optional, List


CHAINLIST_URL = "https://chainid.network/chains.json"


def _fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _first_public_rpc(rpcs: List[str]) -> Optional[str]:
    for rpc in rpcs:
        # skip rpc templates that require keys
        if "${" in rpc:
            continue
        return rpc
    return None


def get_sepolia_rpc() -> Optional[str]:
    """Fetch a public Sepolia RPC endpoint dynamically from chainlist."""
    try:
        data = _fetch_json(CHAINLIST_URL)
        for chain in data:
            if chain.get("chainId") == 11155111:  # Sepolia
                rpc = _first_public_rpc(chain.get("rpc", []))
                if rpc:
                    return rpc
    except Exception:
        pass
    return None


def get_polygon_mumbai_rpc() -> Optional[str]:
    """Fetch a public Polygon Mumbai RPC endpoint dynamically from chainlist."""
    try:
        data = _fetch_json(CHAINLIST_URL)
        for chain in data:
            if chain.get("chainId") == 80001:  # Mumbai
                rpc = _first_public_rpc(chain.get("rpc", []))
                if rpc:
                    return rpc
    except Exception:
        pass
    return None


def get_hedera_mirror_base() -> str:
    """Return Hedera testnet mirror node base. Uses a public mirror; no API key."""
    # If needed, we could probe alternatives by hitting /api/v1/network/nodes
    return "https://testnet.mirrornode.hedera.com"


