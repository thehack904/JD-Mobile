from __future__ import annotations

import os
import time
from typing import Optional

import requests
from flask import Flask, flash, g, redirect, render_template, request, url_for

from .config_manager import ConfigManager
from .providers.local_api import LocalProvider

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    template_folder=os.path.join(_ROOT, "templates"),
    static_folder=os.path.join(_ROOT, "static"),
)
app.secret_key = os.environ.get("FLASK_SECRET", "change-me")

cfg_mgr = ConfigManager()

def _get_active_local_provider():
    res = g.cfg
    inst = cfg_mgr.get_active_instance(res.config)
    if not inst:
        raise RuntimeError("No active instance configured.")
    p = inst.get("providers", {}).get("primary", {})
    if (p.get("type") or "").lower() != "local":
        raise RuntimeError("Primary provider is not local (only local is supported in v0.1).")
    base_url = p.get("base_url") or ""
    timeout_ms = int(p.get("timeout_ms") or 800)
    return LocalProvider(base_url=base_url, timeout_ms=timeout_ms)

def _test_jd_help(base_url: str, timeout_ms: int = 800) -> tuple[bool, str]:
    base_url = (base_url or "").strip().rstrip("/")
    if not base_url:
        return False, "Base URL is empty."
    try:
        r = requests.get(f"{base_url}/help", timeout=max(0.1, timeout_ms / 1000.0))
        if r.status_code != 200:
            return False, f"HTTP {r.status_code} from {base_url}/help"
        # Light validation
        body = r.text.lower()
        if "jdownloader" not in body and "downloads" not in body and "linkgrabber" not in body:
            return True, "Connected (help endpoint reachable), but response did not contain expected keywords."
        return True, "Connected."
    except Exception as e:
        return False, str(e)

@app.before_request
def load_config():
    g.cfg = cfg_mgr.load()
    # Ensure /app/config is writable (common misconfig)
    config_dir = os.path.dirname(g.cfg.path)
    try:
        os.makedirs(config_dir, exist_ok=True)
        test_path = os.path.join(config_dir, ".write_test")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(str(time.time()))
        os.remove(test_path)
        g.config_writable = True
    except Exception:
        g.config_writable = False

    if g.cfg.needs_setup and not request.path.startswith("/setup") and not request.path.startswith("/static"):
        return redirect(url_for("setup"))

@app.get("/setup")
def setup():
    # v0.1: manual setup only. Auto-detect comes in v0.2.
    return render_template(
        "setup.html",
        title=g.cfg.config.get("ui", {}).get("title", "JD-Mobile"),
        cfg=g.cfg,
        config_writable=g.config_writable,
    )

@app.post("/setup/manual")
def setup_manual():
    base_url = (request.form.get("base_url") or "").strip().rstrip("/")
    timeout_ms = int(request.form.get("timeout_ms") or 800)
    name = (request.form.get("name") or "Primary").strip() or "Primary"

    ok, msg = _test_jd_help(base_url, timeout_ms=timeout_ms)
    if not ok:
        flash(f"Connection test failed: {msg}", "danger")
        return redirect(url_for("setup"))

    cfg = g.cfg.config
    # Ensure single instance exists
    if not cfg.get("instances"):
        cfg["instances"] = []
    if len(cfg["instances"]) == 0:
        cfg["instances"].append({
            "id": "primary",
            "name": name,
            "enabled": True,
            "providers": {
                "primary": {"type": "local", "base_url": base_url, "timeout_ms": timeout_ms},
                "fallback": {"type": "myjd", "enabled": False}
            },
        })
        cfg["active_instance_id"] = "primary"
    else:
        inst = cfg["instances"][0]
        inst["name"] = name
        inst.setdefault("providers", {}).setdefault("primary", {})
        inst["providers"]["primary"].update({"type": "local", "base_url": base_url, "timeout_ms": timeout_ms})
        cfg["active_instance_id"] = inst.get("id", "primary")

    saved, errors = cfg_mgr.save(cfg)
    if not saved:
        flash("Failed to save config: " + "; ".join(errors), "danger")
        return redirect(url_for("setup"))

    flash("Saved. Connected to JDownloader.", "success")
    return redirect(url_for("index"))

@app.get("/")
def index():
    provider = _get_active_local_provider()
    try:
        packages = provider.get_packages()
    except Exception as e:
        packages = []
        flash(f"Failed to query packages: {e}", "danger")
    return render_template(
        "index.html",
        title=g.cfg.config.get("ui", {}).get("title", "JD-Mobile"),
        packages=packages,
    )

@app.get("/add")
def add_form():
    return render_template(
        "add.html",
        title=g.cfg.config.get("ui", {}).get("title", "JD-Mobile"),
    )

@app.post("/add")
def add_submit():
    links = (request.form.get("links") or "").strip()
    package = (request.form.get("package") or "Mobile").strip()
    dest = (request.form.get("dest") or "").strip() or None
    autostart = (request.form.get("autostart") == "on")

    if not links:
        flash("Paste one or more links.", "warning")
        return redirect(url_for("add_form"))

    provider = _get_active_local_provider()
    try:
        provider.add_links(links=links, package=package, dest=dest, autostart=autostart)
        flash("Links submitted to LinkGrabber.", "success")
    except Exception as e:
        flash(f"Failed to add links: {e}", "danger")

    return redirect(url_for("index"))

@app.post("/remove")
def remove_package():
    pkg_id = request.form.get("package_id")
    delete_files = request.form.get("delete_files") == "true"
    if not pkg_id:
        flash("No package specified.", "warning")
        return redirect(url_for("index"))
    try:
        pkg_id_int = int(pkg_id)
    except (ValueError, TypeError):
        flash("Invalid package ID.", "danger")
        return redirect(url_for("index"))

    provider = _get_active_local_provider()
    try:
        if delete_files:
            provider.cleanup_packages([pkg_id_int])
            flash("Package removed and files deleted.", "success")
        else:
            provider.remove_packages([pkg_id_int])
            flash("Package removed (files kept on disk).", "success")
    except Exception as e:
        flash(f"Failed to remove package: {e}", "danger")

    return redirect(url_for("index"))

@app.get("/health")
def health():
    if g.cfg.needs_setup:
        return {"ok": False, "needs_setup": True, "config_path": g.cfg.path, "writable": g.config_writable}, 503
    inst = cfg_mgr.get_active_instance(g.cfg.config) or {}
    p = (inst.get("providers") or {}).get("primary") or {}
    base_url = p.get("base_url") or ""
    ok, msg = _test_jd_help(base_url, timeout_ms=int(p.get("timeout_ms") or 800))
    return {"ok": ok, "message": msg, "base_url": base_url, "config_path": g.cfg.path, "writable": g.config_writable}, (200 if ok else 502)
