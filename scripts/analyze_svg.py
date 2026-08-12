#!/usr/bin/env python3
"""Print the measurements used by the README comparison table."""

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ElementTree


COMMANDS = re.compile(
    r"([AaCcHhLlMmQqSsTtVvZz])([^AaCcHhLlMmQqSsTtVvZz]*)"
)
NUMBERS = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
# Numeric parameters consumed by one SVG path command:
# A = radii, rotation, flags, and endpoint; C = two control points and endpoint;
# H/V = one axis; L/M/T = endpoint; Q/S = control point and endpoint.
# The parser divides each command's numbers by these counts to detect repeated
# segments. Z is omitted because closing a path consumes no parameters.
PARAMETER_COUNTS = {
    "A": 7,
    "C": 6,
    "H": 1,
    "L": 2,
    "M": 2,
    "Q": 4,
    "S": 4,
    "T": 2,
    "V": 1,
}


def git(*arguments):
    """Run Git and return its standard output."""
    result = subprocess.run(
        ["git", *arguments],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.decode("utf-8", errors="replace").strip()
        )
    return result.stdout


def first_commit(path):
    """Find the first commit in the file's history."""
    output = git(
        "log", "--follow", "--reverse", "--format=%H", "--", path
    )
    commits = output.decode("ascii").splitlines()
    if not commits:
        raise RuntimeError(f"No committed history found for {path}")
    return commits[0]


def path_counts(path_data):
    """Count nodes and segments in one SVG path."""
    counts = {
        "nodes": 0,
        "cubic_segments": 0,
        "line_segments": 0,
        "closed_subpaths": 0,
    }

    for raw_command, raw_values in COMMANDS.findall(path_data):
        command = raw_command.upper()
        if command == "Z":
            counts["closed_subpaths"] += 1
            continue

        value_count = len(NUMBERS.findall(raw_values))
        group_count = value_count // PARAMETER_COUNTS[command]
        counts["nodes"] += group_count

        if command in {"C", "S"}:
            counts["cubic_segments"] += group_count
        elif command in {"H", "L", "V"}:
            counts["line_segments"] += group_count
        elif command == "M":
            counts["line_segments"] += max(0, group_count - 1)

    return counts


def local_name(name):
    """Remove an XML namespace from a tag or attribute name."""
    return name.rsplit("}", maxsplit=1)[-1]


def analyze(content):
    """Measure one SVG document."""
    root = ElementTree.fromstring(content)
    elements = list(root.iter())
    paths = [
        element for element in elements if local_name(element.tag) == "path"
    ]
    per_path = [path_counts(path.attrib["d"]) for path in paths]
    node_types = "".join(
        value
        for element in elements
        for name, value in element.attrib.items()
        if local_name(name) == "nodetypes"
    )

    return {
        "total_path_nodes": sum(item["nodes"] for item in per_path),
        "symbol_nodes": per_path[1]["nodes"],
        "cubic_segments": sum(
            item["cubic_segments"] for item in per_path
        ),
        "line_segments": sum(item["line_segments"] for item in per_path),
        "paths": len(paths),
        "closed_subpaths": sum(
            item["closed_subpaths"] for item in per_path
        ),
        "canvas": f"{root.attrib['width']} x {root.attrib['height']}",
        "viewBox": root.attrib.get("viewBox", "Not set"),
        "colors": ", ".join(path.attrib["fill"] for path in paths),
        "node_types": (
            f"{node_types.count('c')} corner, "
            f"{node_types.count('s')} smooth"
            if node_types
            else "Not recorded"
        ),
        "xml_elements": len(elements),
        "file_bytes": len(content),
    }


def print_row(name, before, after):
    """Print one tab-separated comparison row."""
    print(f"{name}\t{before}\t{after}")


def main():
    """Run the command-line comparison."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default="bitcoin.svg")
    parser.add_argument("--before")
    parser.add_argument("--after", default="HEAD")
    arguments = parser.parse_args()

    before_ref = arguments.before or first_commit(arguments.path)
    before_commit = git("rev-parse", before_ref).decode("ascii").strip()
    after_commit = git("rev-parse", arguments.after).decode("ascii").strip()
    before = analyze(git("show", f"{before_commit}:{arguments.path}"))
    after = analyze(git("show", f"{after_commit}:{arguments.path}"))
    edit_count = git(
        "rev-list",
        "--count",
        f"{before_commit}..{after_commit}",
        "--",
        arguments.path,
    ).decode("ascii").strip()

    print(f"Before commit: {before_commit}")
    print(f"After commit:  {after_commit}")
    print(f"SVG-editing commits after before: {edit_count}")
    print()
    print("property\tbefore\tafter")
    for name in before:
        print_row(name, before[name], after[name])


if __name__ == "__main__":
    try:
        main()
    except (IndexError, KeyError, RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(1)
