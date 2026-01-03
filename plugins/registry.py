from __future__ import annotations

from typing import Dict
from threading import Lock

import logging

from .interface import AgentPlugin, GeneratorPlugin, RefinerPlugin


class PluginRegistry:
    """Registry for generator and refiner plug-ins."""

    def __init__(self) -> None:
        self.generators: Dict[str, GeneratorPlugin] = {}
        self.refiners: Dict[str, RefinerPlugin] = {}
        self._lock = Lock()

    def register(self, plugin: AgentPlugin) -> None:
        """Register a plug-in instance based on its kind."""
        with self._lock:
            if plugin.name in self.generators or plugin.name in self.refiners:
                logging.error("Duplicate plug-in registration: %s", plugin.name)
                raise ValueError(f"Plugin '{plugin.name}' already registered")
            if isinstance(plugin, GeneratorPlugin):
                self.generators[plugin.name] = plugin
            elif isinstance(plugin, RefinerPlugin):
                self.refiners[plugin.name] = plugin
            else:
                raise TypeError("Unknown plug-in type")

    def unregister(self, name: str) -> None:
        """Remove a plug-in by name."""
        plugin: AgentPlugin | None = None
        with self._lock:
            if name in self.generators:
                plugin = self.generators.pop(name)
            elif name in self.refiners:
                plugin = self.refiners.pop(name)
        if plugin is None:
            return
        plugin.cleanup()

    def get_generator(self, name: str) -> GeneratorPlugin:
        return self.generators[name]

    def get_refiner(self, name: str) -> RefinerPlugin:
        return self.refiners[name]


# Global registry instance used by the agent system
registry = PluginRegistry()
