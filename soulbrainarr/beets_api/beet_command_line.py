import re
import subprocess

from soulbrainarr.config_parser import CONFIG


def run_beet_command(args: list[str], run_non_interactive: bool = True) -> tuple[str, str]:
    """
    Explicitly uses the provided config.yaml and library.db paths.
    Returns (stdout, stderr).
    """
    cmd = [
        "beet",
        "-c", CONFIG.BEETS.BEETS_CONFIG,
        "-l", CONFIG.BEETS.BEETS_DATABASE,
    ]

    if run_non_interactive:
        cmd += ["-q"]

    cmd += args

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    standard_output, error_output = process.communicate()
    return standard_output, error_output


def parse_failed_imports_from_error_string(output: str) -> list[str]:
    """
    Parses beets import output and returns file paths
    that were skipped or failed to import.
    """
    failed_patterns = [
        "Skipping",
        "No match found",
        r"\[F\]",
        r"\[D\]",
    ]

    path_regex = re.compile(r"(/[^:\n]+)")

    failed = []

    for line in output.splitlines():
        if any(pattern in line for pattern in failed_patterns):
            regex_search_result = path_regex.search(line)
            if regex_search_result:
                failed.append(regex_search_result.group(1))

    return failed
