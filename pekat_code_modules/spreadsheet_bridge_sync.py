"""PEKAT Code tool bridge pro synchronn? evaluaci Easysheet backendem.

Skript je z?m?rn? bez extern?ch z?vislost?. V PEKAT Code toolu mus? bezpe?n?
prob?hnout i tehdy, kdy? backend neb??? nebo v Contextu chyb? o?ek?van? kl??e.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"
DEFAULT_PROJECT_ID = "Camera_1"
DEFAULT_TIMEOUT_S = 0.3


def _json_safe(value: Any) -> Any:
    """P?evede b??n? PEKAT/NumPy objekty na JSON-safe reprezentaci.

    Obrazov? data nepos?l?me cel?. Pro `np.ndarray` sta?? metadata tvaru a typu,
    aby snapshot z?stal mal? a Code tool nezdr?oval aktu?ln? FLOW.
    """

    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    shape = getattr(value, "shape", None)
    dtype = getattr(value, "dtype", None)
    if shape is not None:
        return {
            "type": type(value).__name__,
            "shape": list(shape),
            "dtype": str(dtype) if dtype is not None else None,
        }
    return str(value)


def _build_snapshot(context: dict[str, Any], module_item: dict[str, Any]) -> dict[str, Any]:
    """Sestav? minim?ln? snapshot pro backend."""

    project_id = str(module_item.get("project_id") or DEFAULT_PROJECT_ID)
    frame_id = str(
        module_item.get("frame_id")
        or context.get("frame_id")
        or context.get("frameId")
        or f"{project_id}_{int(time.time() * 1000)}"
    )
    global_data = context.get("global_data") or context.get("globalData") or {}
    return {
        "project_id": project_id,
        "frame_id": frame_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": str(module_item.get("mode") or "sync"),
        "context": _json_safe(context),
        "global_data": _json_safe(global_data),
    }


def _post_json(url: str, payload: dict[str, Any], timeout_s: float) -> dict[str, Any]:
    """Ode?le JSON request p?es stdlib urllib s explicitn?m timeoutem."""

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def _deep_merge(target: dict[str, Any], updates: dict[str, Any]) -> None:
    """Rekurzivn? slou?? slovn?kov? aktualizace bez zm?ny existuj?c?ch typ?."""

    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value


def _apply_response(context: dict[str, Any], response: dict[str, Any]) -> None:
    """Zap??e odpov?? backendu zp?t do PEKAT Contextu."""

    updates = response.get("context_updates") or {}
    if isinstance(updates, dict):
        _deep_merge(context, updates)

    global_updates = response.get("global_updates") or {}
    if isinstance(global_updates, dict) and global_updates:
        global_key = "global_data" if "globalData" not in context else "globalData"
        if not isinstance(context.get(global_key), dict):
            context[global_key] = {}
        _deep_merge(context[global_key], global_updates)

    control = response.get("control") or {}
    if isinstance(control, dict):
        if control.get("exit") is True:
            context["exit"] = True
        if control.get("override_result") is not None:
            context["result"] = bool(control["override_result"])


def _write_failure(context: dict[str, Any], error: Exception) -> None:
    """Zap??e diagnostiku p?i chyb? backendu bez shozen? PEKAT FLOW."""

    fallback_result = bool(context.get("result", True))
    context["spreadsheet"] = {
        "result": fallback_result,
        "reason": "BACKEND_UNAVAILABLE",
        "error": f"{type(error).__name__}: {error}",
        "outputs": {
            "master_result": fallback_result,
            "allow_branch_default": fallback_result,
        },
    }


def main(context: dict[str, Any], module_item: dict[str, Any] | None = None) -> None:
    """PEKAT Code tool entrypoint.

    `module_item` odpov?d? hodnot?m z Form Editoru. Funkce nikdy v?dom?
    nevyhazuje v?jimku ven, aby jeden timeout backendu nezablokoval inspekci.
    """

    if not isinstance(context, dict):
        return

    settings = module_item if isinstance(module_item, dict) else {}
    backend_url = str(settings.get("backend_url") or DEFAULT_BACKEND_URL).rstrip("/")
    timeout_s = float(settings.get("timeout_s") or DEFAULT_TIMEOUT_S)

    try:
        snapshot = _build_snapshot(context, settings)
        response = _post_json(f"{backend_url}/api/evaluate", snapshot, timeout_s)
        _apply_response(context, response)
    except (OSError, ValueError, urllib.error.URLError, TimeoutError) as exc:
        _write_failure(context, exc)
