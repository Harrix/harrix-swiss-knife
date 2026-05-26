"""Re-export BotHub network helpers from integrations.bothub (backward compatibility)."""

from harrix_swiss_knife.integrations.bothub.network import qnetwork_proxy_to_url, resolve_bothub_proxy_url

__all__ = ["qnetwork_proxy_to_url", "resolve_bothub_proxy_url"]
