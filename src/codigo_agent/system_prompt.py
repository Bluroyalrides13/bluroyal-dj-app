"""
System prompt for the Código de Poder 777 sales agent.

The prompt text itself lives in docs/codigo_sales_brain.md so Cindy (or
Claude) can edit the sales logic without touching code. This module just
loads it as a string constant, with a fallback if the file is ever moved.
"""

from pathlib import Path

_BRAIN_PATH = Path(__file__).resolve().parents[2] / "docs" / "codigo_sales_brain.md"

try:
    SYSTEM_PROMPT = _BRAIN_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    SYSTEM_PROMPT = (
        "Eres el agente de ventas de Código de Poder 777. "
        "ADVERTENCIA: docs/codigo_sales_brain.md no se encontró — "
        "este es un prompt de respaldo mínimo. Restaura el archivo "
        "para recuperar el catálogo completo y las reglas de venta."
    )

