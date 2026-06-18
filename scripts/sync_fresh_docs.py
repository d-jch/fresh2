"""Synchronize Fresh docs/latest into this plugin's references directory."""

from __future__ import annotations

import argparse
import base64
import json
import posixpath
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Iterable


OWNER = "freshframework"
REPO = "fresh"
DOCS_ROOT = PurePosixPath("docs/latest")
DEFAULT_REF = "main"
RAW_DOCS_BASE_URL = (
    f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{DEFAULT_REF}/{DOCS_ROOT}"
)
ARCHIVE_URL_TEMPLATE = f"https://codeload.github.com/{OWNER}/{REPO}/zip/refs/heads/{{ref}}"

MARKDOWN_LINK_RE = re.compile(r"(!?\[[^\]]*\]\()([^)\s#]+)((?:#[^)\s]+)?)(\))")


@dataclass(frozen=True)
class RemoteMarkdownFile:
    path: PurePosixPath
    download_url: str


def _is_external_target(target: str) -> bool:
    return (
        target.startswith("#")
        or target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
    )


def _split_docs_target(target: str) -> str | None:
    if target.startswith("/docs/latest/"):
        return target.removeprefix("/docs/latest/")
    if target == "/docs/latest":
        return "index"
    if target.startswith("/docs/"):
        return target.removeprefix("/docs/")
    if target == "/docs":
        return "index"
    return None


def _candidate_markdown_paths(path: PurePosixPath) -> list[PurePosixPath]:
    normalized = PurePosixPath(posixpath.normpath(path.as_posix()))
    candidates = [normalized]
    if normalized.suffix == "":
        candidates.append(normalized.with_suffix(".md"))
        candidates.append(normalized / "index.md")
    return candidates


def _resolve_doc_path(
    target: str,
    current_file: PurePosixPath,
    doc_files: set[PurePosixPath],
) -> PurePosixPath | None:
    docs_target = _split_docs_target(target)
    if docs_target is not None:
        bases = [PurePosixPath(docs_target)]
    elif target.startswith("/"):
        return None
    else:
        bases = [
            current_file.parent / target,
            PurePosixPath(target.removeprefix("./")),
        ]

    for base in bases:
        for candidate in _candidate_markdown_paths(base):
            if candidate in doc_files:
                return candidate
    return None


def _is_asset_target(target: str) -> bool:
    suffix = PurePosixPath(target).suffix.lower()
    return suffix in {
        ".avif",
        ".gif",
        ".jpeg",
        ".jpg",
        ".png",
        ".svg",
        ".webp",
    }


def _relative_link(from_file: PurePosixPath, to_file: PurePosixPath) -> str:
    start = from_file.parent.as_posix()
    if start == ".":
        start = ""
    rel = posixpath.relpath(to_file.as_posix(), start=start or ".")
    return rel if rel.startswith(".") else rel


def rewrite_markdown_links(
    text: str,
    *,
    current_file: PurePosixPath,
    doc_files: set[PurePosixPath],
    raw_docs_base_url: str = RAW_DOCS_BASE_URL,
) -> str:
    """Rewrite Fresh docs links for local plugin references."""

    def replace(match: re.Match[str]) -> str:
        prefix, target, anchor, suffix = match.groups()
        if _is_external_target(target):
            return match.group(0)

        docs_target = _split_docs_target(target)
        if docs_target is not None and _is_asset_target(docs_target):
            raw_target = f"{raw_docs_base_url}/{docs_target.lstrip('/')}"
            return f"{prefix}{raw_target}{anchor}{suffix}"

        resolved = _resolve_doc_path(target, current_file, doc_files)
        if resolved is None:
            return match.group(0)

        return f"{prefix}{_relative_link(current_file, resolved)}{anchor}{suffix}"

    return MARKDOWN_LINK_RE.sub(replace, text)


def _github_api_url(path: PurePosixPath, ref: str) -> str:
    return (
        f"https://api.github.com/repos/{OWNER}/{REPO}/contents/"
        f"{path.as_posix()}?ref={ref}"
    )


def _fetch_json(url: str) -> object:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "fresh2-doc-sync",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        completed = subprocess.run(
            ["curl", "-fsSL", "--retry", "3", "--retry-delay", "1", url],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return json.loads(completed.stdout.decode("utf-8"))


def _fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "fresh2-doc-sync"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.URLError:
        completed = subprocess.run(
            ["curl", "-fsSL", "--retry", "3", "--retry-delay", "1", url],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout


def _fetch_markdown_file(path: PurePosixPath, *, ref: str) -> str:
    payload = _fetch_json(_github_api_url(DOCS_ROOT / path, ref))
    if not isinstance(payload, dict) or payload.get("encoding") != "base64":
        raise RuntimeError(f"Expected base64 file payload for {path}")
    content = payload.get("content")
    if not isinstance(content, str):
        raise RuntimeError(f"Missing file content for {path}")
    return base64.b64decode(content).decode("utf-8")


def extract_markdown_files_from_archive(archive_bytes: bytes) -> dict[PurePosixPath, str]:
    docs_prefix = f"{DOCS_ROOT.as_posix()}/"
    files: dict[PurePosixPath, str] = {}
    with zipfile.ZipFile(BytesIO(archive_bytes)) as archive:
        for name in archive.namelist():
            if name.endswith("/"):
                continue
            parts = name.split("/", 1)
            if len(parts) != 2:
                continue
            inner = parts[1]
            if not inner.startswith(docs_prefix) or not inner.endswith(".md"):
                continue
            relative = PurePosixPath(inner.removeprefix(docs_prefix))
            files[relative] = archive.read(name).decode("utf-8")
    if not files:
        raise RuntimeError("No Markdown files found under docs/latest in archive")
    return files


def list_remote_markdown_files(
    path: PurePosixPath = DOCS_ROOT,
    *,
    ref: str = DEFAULT_REF,
) -> list[RemoteMarkdownFile]:
    payload = _fetch_json(_github_api_url(path, ref))
    if not isinstance(payload, list):
        raise RuntimeError(f"Expected directory listing for {path}")

    files: list[RemoteMarkdownFile] = []
    for item in payload:
        item_type = item.get("type")
        item_path = PurePosixPath(item["path"])
        if item_type == "dir":
            files.extend(list_remote_markdown_files(item_path, ref=ref))
        elif item_type == "file" and item_path.suffix == ".md":
            relative = item_path.relative_to(DOCS_ROOT)
            files.append(RemoteMarkdownFile(relative, item["download_url"]))
    return sorted(files, key=lambda file: file.path.as_posix())


def build_index(files: Iterable[PurePosixPath]) -> str:
    lines = [
        "# Fresh 2 Documentation Reference Index",
        "",
        "Generated from `freshframework/fresh` `docs/latest`.",
        "",
    ]
    for path in sorted(files, key=lambda item: item.as_posix()):
        if path == PurePosixPath("INDEX.md"):
            continue
        title = path.with_suffix("").as_posix().replace("-", " ").replace("/", " / ")
        lines.append(f"- [{title}]({path.as_posix()})")
    lines.append("")
    return "\n".join(lines)


def sync_docs(destination: Path, *, ref: str, dry_run: bool, verbose: bool) -> int:
    if ref == DEFAULT_REF:
        archive_url = ARCHIVE_URL_TEMPLATE.format(ref=ref)
    else:
        archive_url = f"https://codeload.github.com/{OWNER}/{REPO}/zip/{ref}"
    if verbose:
        print(f"fetch archive {archive_url}", file=sys.stderr)
    archive_files = extract_markdown_files_from_archive(_fetch_bytes(archive_url))
    doc_files = set(archive_files)
    rewritten: dict[PurePosixPath, str] = {}

    for path, raw_text in sorted(archive_files.items()):
        if verbose:
            print(f"rewrite {path}", file=sys.stderr)
        rewritten[path] = rewrite_markdown_links(
            raw_text,
            current_file=path,
            doc_files=doc_files,
            raw_docs_base_url=RAW_DOCS_BASE_URL.replace(f"/{DEFAULT_REF}/", f"/{ref}/"),
        )

    rewritten[PurePosixPath("INDEX.md")] = build_index(doc_files)

    if dry_run:
        for path in sorted(rewritten):
            print(path.as_posix())
        return len(rewritten)

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    for path, content in rewritten.items():
        out = destination / Path(path.as_posix())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")

    print(f"Wrote {len(rewritten)} files to {destination}")
    return len(rewritten)


def sync_local_docs(source_dir: Path, destination: Path, *, dry_run: bool) -> int:
    remote_files = [
        path.relative_to(source_dir)
        for path in source_dir.rglob("*.md")
        if path.name != "INDEX.md"
    ]
    doc_files = {PurePosixPath(path.as_posix()) for path in remote_files}
    rewritten: dict[PurePosixPath, str] = {}

    for path in sorted(doc_files):
        raw_text = (source_dir / Path(path.as_posix())).read_text(encoding="utf-8")
        rewritten[path] = rewrite_markdown_links(
            raw_text,
            current_file=path,
            doc_files=doc_files,
        )

    rewritten[PurePosixPath("INDEX.md")] = build_index(doc_files)

    if dry_run:
        for path in sorted(rewritten):
            print(path.as_posix())
        return len(rewritten)

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    for path, content in rewritten.items():
        out = destination / Path(path.as_posix())
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")

    print(f"Wrote {len(rewritten)} files to {destination}")
    return len(rewritten)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destination",
        default="skills/fresh2/references",
        help="Directory to replace with synchronized references.",
    )
    parser.add_argument("--ref", default=DEFAULT_REF, help="Git ref to download.")
    parser.add_argument(
        "--source-dir",
        help="Rewrite Markdown from an existing local docs directory instead of GitHub.",
    )
    parser.add_argument("--dry-run", action="store_true", help="List files only.")
    parser.add_argument("--verbose", action="store_true", help="Print fetch progress.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.source_dir:
            sync_local_docs(
                Path(args.source_dir),
                Path(args.destination),
                dry_run=args.dry_run,
            )
        else:
            sync_docs(
                Path(args.destination),
                ref=args.ref,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )
    except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
        print(f"fresh docs sync failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
