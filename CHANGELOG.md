# Changelog

## v0.2.0
- **Remove packages** — each package on the Downloads page now has a Remove button.  A confirmation dialog lets you choose to keep or permanently delete the downloaded files from disk. (closes #3)
- **Live auto-refresh** — the Downloads page polls the JD API every 3 seconds and updates package status, progress, ETA, and speed without requiring a manual page reload. (closes #5)
- **Select files before downloading** — when adding links you can enable the "Select files before downloading" toggle. Links are sent to LinkGrabber, then you are taken to a file-selection screen where you can check/uncheck individual files before starting the download. The selection screen also auto-polls every 3 seconds while JDownloader is still crawling the link. (closes #7)

## v0.1.0
- Initial private MVP:
  - Setup wizard (manual host)
  - Add links to LinkGrabber
  - Packages/Downloads overview
  - Persistent config + validation (prevents app crashes)
