# Roadmap

## v0.1 - Local MVP (this repo)
- [x] Mobile-first UI
- [x] Manual setup wizard (single instance)
- [x] Add links (LinkGrabber)
- [x] Packages/Downloads overview
- [x] Persistent config (config.json) with validation to prevent crashes
- [x] Remove packages (keep or delete files from disk)
- [x] Live auto-refresh — Downloads page polls every 3 s, no manual reload needed
- [x] Select specific files before downloading (per-link file picker with auto-poll while JD crawls)
- [ ] Start/stop controls (pending confirmation of endpoints on your pinned JD build)

## v0.2 - Setup Wizard + Smart Discovery
- [ ] Wizard Step 1: Manual vs Auto-detect choice
- [ ] Explicit scan permission + scan scope control (default /24)
- [ ] Validate via `http://HOST:3128/help`
- [ ] Connection test tooling + clearer error UX
- [ ] Reverse-proxy friendly docs (NPM/Traefik)

## v0.3 - Multi-Instance + Unified Control
- [ ] Store and manage multiple JD instances in a single UI
- [ ] Auto-detect accepts multiple subnets / seed hosts
- [ ] Instance switcher + per-instance status badge
- [ ] Offline instance handling (no cross-fire, safe scoping)

## v0.4 - MyJDownloader Fallback Provider
- [ ] Implement MyJDownloader provider
- [ ] Per-instance provider config (Local primary, MyJD fallback)
- [ ] Auto failover (Local -> MyJD) when local unreachable
- [ ] Token caching/refresh, device selection, diagnostics
