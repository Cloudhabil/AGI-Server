# Brahim-Aligned Debugger Agent
# BOA SDK - Coding & Debugging Module

from .agent import BrahimDebuggerAgent
from .engine import BrahimEngine
from .analyzer import CodeAnalyzer
from .fixer import CodeFixer

__version__ = "1.0.0"
__all__ = ["BrahimDebuggerAgent", "BrahimEngine", "CodeAnalyzer", "CodeFixer"]
