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

### Enabling JDownloader's Local API (port 3128)

JDownloader's Local API on port 3128 is a **deprecated but still functional** API that JD-Mobile relies on. It is **not enabled by default** in newer versions of JDownloader 2. Follow these steps to enable it:

1. Open **JDownloader 2**.
2. Go to **Settings** → **Advanced Settings** (the gear icon).
3. In the filter/search field at the top, type `RemoteAPI`.
4. Find `org.jdownloader.api.RemoteAPIConfig.enabled` and set it to **`true`**.
5. Confirm `org.jdownloader.api.RemoteAPIConfig.port` is set to **`3128`**.
6. Restart JDownloader for the changes to take effect.

Verify the API is active by visiting:

```
http://<JD_HOST>:3128/help
```

> **Note:** This is JDownloader's legacy local API (deprecated in favor of MyJDownloader). JD-Mobile requires it to communicate with your local JDownloader instance over LAN/VPN.

> JD-Mobile uses a persistent config file: `/app/config/config.json`.  
> Mount `/app/config` to a host path to keep settings across container upgrades.

## Usage

### Adding links

1. Open JD-Mobile in your browser (`http://<host>:8086`).
2. Tap **Add** in the top-right corner of the Downloads page.
3. Paste one or more URLs into the **Links** box (one per line, or paste a block).
4. *(Optional)* Change the **Package** name or set a custom **Destination** folder.
5. Leave **Autostart** enabled if you want downloads to begin immediately.
6. Tap **Send to LinkGrabber**.  
   The links are queued in JDownloader and the Downloads page will refresh automatically.

### Selecting specific files before downloading

Use this when a link contains multiple files and you only want some of them.

1. On the Add Links page, enable the **"Select files before downloading"** toggle.
2. Tap **Send to LinkGrabber**.
3. You are taken to the **Select files** screen.  
   If JDownloader is still crawling the link the list will refresh automatically every few seconds — wait for all files to appear.
4. Check the files you want to download and uncheck the ones you do not.  
   Use the **All** / **None** buttons to quickly select or deselect everything.
5. Tap **Start selected downloads** to move the checked files to the download queue.  
   Unchecked files are automatically removed from the LinkGrabber queue.
6. Tap **Discard all & cancel** if you change your mind and want to clear everything.

### Monitoring downloads (live auto-refresh)

The Downloads page polls JDownloader every **3 seconds** and automatically updates:

- Package name and current status (`IDLE`, `RUN`, `DONE`)
- Downloaded / total size (MB)
- ETA and current speed

No manual page refresh is needed.

### Removing a package

1. On the Downloads page, find the package you want to remove.
2. Tap the red **Remove** button next to it.
3. A dialog will ask what to do with the downloaded files:
   - **Keep all downloaded files on hard disk** — removes the package from JDownloader but leaves the files in place.
   - **Delete downloaded files from hard disk** — removes the package *and* permanently deletes the associated files.
4. Tap your choice to confirm.

## TrueNAS (recommended bind mount)

Set `JD_MOBILE_HOST_CONFIG_DIR` in `.env` to a dataset path such as:

- `/mnt/tank/apps/jd-mobile/config`

Then JD-Mobile will persist its config at:

- `/mnt/tank/apps/jd-mobile/config/config.json`

## Features (v0.2)

- Setup wizard (manual host entry)
- Add links (LinkGrabber)
- **Select specific files** from a pasted link before downloading
- Packages overview (Downloads) with **live auto-refresh** (no manual reload needed)
- **Remove packages** — keep or delete files from disk

## Security

- Do **not** expose port 3128 publicly.
- Access JD-Mobile over LAN/VPN.
- Optionally place JD-Mobile behind a reverse proxy with auth.

## License

MIT (see LICENSE).
