"""
CS Network module - Customer Service Network Application.
Provides network-related customer service functionality.
"""

# Import hauptkomponenten für einfacheren Zugriff
try:
    from .state import GraphState
except ImportError:
    pass

try:
    from .node import triage_agent
except ImportError:
    pass

# Weitere Module können hier exportiert werden
__all__ = [
    'GraphState',
    'triage_agent',
]
