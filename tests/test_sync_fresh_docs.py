import unittest
import zipfile
from io import BytesIO
from pathlib import PurePosixPath
from subprocess import CompletedProcess
from unittest import mock
from urllib.error import URLError

from scripts.sync_fresh_docs import (
    RAW_DOCS_BASE_URL,
    _fetch_json,
    extract_markdown_files_from_archive,
    rewrite_markdown_links,
)


DOC_FILES = {
    PurePosixPath("concepts/file-routing.md"),
    PurePosixPath("advanced/vite.md"),
    PurePosixPath("testing/index.md"),
    PurePosixPath("examples/api-routes.md"),
}


class RewriteMarkdownLinksTest(unittest.TestCase):
    def test_rewrites_docs_absolute_links_to_relative_markdown_files(self):
        text = (
            "[File Routing](/docs/concepts/file-routing) and "
            "[Testing](/docs/testing)"
        )

        result = rewrite_markdown_links(
            text,
            current_file=PurePosixPath("getting-started/index.md"),
            doc_files=DOC_FILES,
        )

        self.assertEqual(
            result,
            "[File Routing](../concepts/file-routing.md) and "
            "[Testing](../testing/index.md)",
        )

    def test_rewrites_docs_latest_links(self):
        text = "[Vite](/docs/latest/advanced/vite#configuration)"

        result = rewrite_markdown_links(
            text,
            current_file=PurePosixPath("concepts/file-routing.md"),
            doc_files=DOC_FILES,
        )

        self.assertEqual(result, "[Vite](../advanced/vite.md#configuration)")

    def test_rewrites_root_relative_links_when_current_relative_path_is_invalid(self):
        text = "[API Routes](./examples/api-routes)"

        result = rewrite_markdown_links(
            text,
            current_file=PurePosixPath("examples/index.md"),
            doc_files=DOC_FILES,
        )

        self.assertEqual(result, "[API Routes](api-routes.md)")

    def test_rewrites_docs_asset_links_to_raw_github_urls(self):
        text = "![Diagram](/docs/architecture-flow-v2.svg)"

        result = rewrite_markdown_links(
            text,
            current_file=PurePosixPath("concepts/architecture.md"),
            doc_files=DOC_FILES,
        )

        self.assertEqual(
            result,
            f"![Diagram]({RAW_DOCS_BASE_URL}/architecture-flow-v2.svg)",
        )

    def test_preserves_external_urls_and_anchors(self):
        text = "[Deno](https://deno.com) and [Local](#section)"

        result = rewrite_markdown_links(
            text,
            current_file=PurePosixPath("concepts/app.md"),
            doc_files=DOC_FILES,
        )

        self.assertEqual(result, text)


class FetchJsonTest(unittest.TestCase):
    def test_uses_curl_fallback_when_urllib_fails(self):
        completed = CompletedProcess(
            args=["curl"],
            returncode=0,
            stdout=b'{"ok": true}',
            stderr=b"",
        )

        with mock.patch("scripts.sync_fresh_docs.urllib.request.urlopen") as urlopen:
            urlopen.side_effect = URLError("tls failed")
            with mock.patch("scripts.sync_fresh_docs.subprocess.run") as run:
                run.return_value = completed

                result = _fetch_json("https://api.github.com/test")

        self.assertEqual(result, {"ok": True})
        run.assert_called_once()
        curl_args = run.call_args.args[0]
        self.assertIn("--retry", curl_args)


class ArchiveExtractionTest(unittest.TestCase):
    def test_extracts_docs_latest_markdown_files_from_github_zip(self):
        archive = BytesIO()
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("fresh-main/docs/latest/concepts/app.md", "# App")
            zf.writestr("fresh-main/docs/latest/testing/index.md", "# Testing")
            zf.writestr("fresh-main/docs/latest/architecture-flow-v2.svg", "<svg />")
            zf.writestr("fresh-main/README.md", "# Repo")

        files = extract_markdown_files_from_archive(archive.getvalue())

        self.assertEqual(
            files,
            {
                PurePosixPath("concepts/app.md"): "# App",
                PurePosixPath("testing/index.md"): "# Testing",
            },
        )


if __name__ == "__main__":
    unittest.main()
