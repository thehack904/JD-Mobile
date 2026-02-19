# JD-Mobile

JD-Mobile is a **self-hosted, mobile-friendly web UI** for controlling a local **JDownloader** instance from your phone/tablet over LAN/VPN.

## Key goals

- **Local-first** control via JDownloader Local API (port **3128**)  
- **Mobile-friendly UI** (not a desktop UI in a phone browser)
- **Persistent config** stored under `/app/config` (survives restarts/upgrades with a bind mount)
- Roadmap: **MyJDownloader cloud fallback** provider

## Quick start (Docker Compose)

1. Copy `.env.example` to `.env` and edit values.
2. Run:

```bash
docker compose up -d --build
```

Open:

- `http://<host>:8086`

### Requirements

- JDownloader must have its Local API enabled and reachable from JD-Mobile.
- Test JD API directly:

```
http://<JD_HOST>:3128/help
```

> JD-Mobile uses a persistent config file: `/app/config/config.json`.  
> Mount `/app/config` to a host path to keep settings across container upgrades.

## TrueNAS (recommended bind mount)

Set `JD_MOBILE_HOST_CONFIG_DIR` in `.env` to a dataset path such as:

- `/mnt/tank/apps/jd-mobile/config`

Then JD-Mobile will persist its config at:

- `/mnt/tank/apps/jd-mobile/config/config.json`

## Features (v0.1)

- Setup wizard (manual host entry)
- Add links (LinkGrabber)
- Packages overview (Downloads)

## Security

- Do **not** expose port 3128 publicly.
- Access JD-Mobile over LAN/VPN.
- Optionally place JD-Mobile behind a reverse proxy with auth.

## License

MIT (see LICENSE).
