"""Re-export BotHub worker from integrations.bothub (backward compatibility)."""

from harrix_swiss_knife.integrations.bothub.worker import BothubChatWorker

__all__ = ["BothubChatWorker"]
