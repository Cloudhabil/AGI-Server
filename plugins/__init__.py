"""Plug-in system for extending agent functionality."""

from .interface import AgentPlugin, GeneratorPlugin, RefinerPlugin
from .registry import PluginRegistry, registry

__all__ = [
    "AgentPlugin",
    "GeneratorPlugin",
    "RefinerPlugin",
    "PluginRegistry",
    "registry",
]
