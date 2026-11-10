"""Get Fitzpatrick17k images and check each one against its MD5 fingerprint.

Two sources:
  * the original atlas URLs listed in the metadata (default). Many DermaAmin links are
    now broken, so this yields only part of the dataset.
  * the full image archive supplied by the dataset authors on request
    (https://github.com/mattgroh/fitzpatrick17k): pass --archive with a .zip, .tar(.gz)
    or folder. Images are matched by file content, so their names inside it don't matter.

Every image is saved as data/raw/images/<md5hash>.jpg, and only kept if its MD5 matches
the metadata. A log of what was found and what was missing is written alongside.

Examples:
    python scripts/download_images.py
    python scripts/download_images.py --archive ~/Downloads/fitzpatrick17k_images.zip
"""

from __future__ import annotations

import argparse
import hashlib
import tarfile
import time
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from tqdm import tqdm

IMAGE_EXTS = (".jpg", ".jpeg", ".png")


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def fetch(url: str, timeout: float, retries: int = 2) -> tuple[bytes | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research dataset download)"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), "ok"
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410):
                return None, f"http {e.code}"
            status = f"http {e.code}"
        except Exception as e:  # network errors, timeouts
            status = type(e).__name__
        time.sleep(1 + attempt)
    return None, status


def from_urls(meta: pd.DataFrame, out: Path, workers: int, timeout: float) -> list[dict]:
    todo = meta[meta["url"].notna() & ~meta["md5hash"].map(lambda h: (out / f"{h}.jpg").exists())]
    log = [{"md5hash": h, "status": "already present"} for h in meta["md5hash"] if (out / f"{h}.jpg").exists()]

    def job(row) -> dict:
        data, status = fetch(row.url, timeout)
        if data is not None:
            if md5(data) != row.md5hash:
                status = "md5 mismatch"
            else:
                (out / f"{row.md5hash}.jpg").write_bytes(data)
        return {"md5hash": row.md5hash, "status": status}

    with ThreadPoolExecutor(workers) as pool:
        futures = [pool.submit(job, row) for row in todo.itertuples()]
        for f in tqdm(as_completed(futures), total=len(futures), desc="downloading"):
            log.append(f.result())
    return log


def iter_archive(path: Path):
    """Yield the bytes of every image file in a zip, tar or folder."""
    if path.is_dir():
        for f in path.rglob("*"):
            if f.suffix.lower() in IMAGE_EXTS:
                yield f.read_bytes()
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if name.lower().endswith(IMAGE_EXTS) and "__MACOSX" not in name:
                    yield zf.read(name)
    elif tarfile.is_tarfile(path):
        with tarfile.open(path) as tf:
            for m in tf:
                if m.isfile() and m.name.lower().endswith(IMAGE_EXTS):
                    yield tf.extractfile(m).read()
    else:
        raise SystemExit(f"{path} is not a folder, zip or tar archive")


def from_archive(meta: pd.DataFrame, out: Path, archive: Path) -> list[dict]:
    wanted = set(meta["md5hash"])
    found = set()
    for data in tqdm(iter_archive(archive), desc=f"scanning {archive.name}"):
        h = md5(data)
        if h in wanted and h not in found:
            (out / f"{h}.jpg").write_bytes(data)
            found.add(h)
    present = {h for h in wanted if (out / f"{h}.jpg").exists()}
    return [{"md5hash": h, "status": "ok" if h in present else "not in archive"} for h in sorted(wanted)]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    p.add_argument("--archive", type=Path, default=None, help="Full image archive from the dataset authors.")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--timeout", type=float, default=30)
    p.add_argument("--limit", type=int, default=None, help="Only try N images (for testing).")
    args = p.parse_args()

    meta = pd.read_csv(args.raw_dir / "Fitzpatrick17k-C.csv", usecols=["md5hash", "url"])
    if args.limit:
        meta = meta.sample(args.limit, random_state=0)
    out = args.raw_dir / "images"
    out.mkdir(parents=True, exist_ok=True)

    log = from_archive(meta, out, args.archive.expanduser()) if args.archive else \
        from_urls(meta, out, args.workers, args.timeout)
    log = pd.DataFrame(log)
    log.to_csv(args.raw_dir / "download_log.csv", index=False)
    have = sum((out / f"{h}.jpg").exists() for h in meta["md5hash"])
    print(f"\n{have} of {len(meta)} images available in {out}")
    print(log["status"].value_counts().to_string())


if __name__ == "__main__":
    main()
