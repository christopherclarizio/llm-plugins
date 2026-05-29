#!/usr/bin/env python3
"""
Flatten plugins from source subtrees into the plugins directory and generate
a unified marketplace.json at the repo root.
"""

import json
import os
import shutil
import sys
from pathlib import Path

# ============================================================================
# PLUGINS MAPPING - Configure which plugins to copy and from where
# ============================================================================
# Format: source_dir (containing plugin subdirectories) -> list of plugin names
# Use "*" to copy all plugins from the source directory.
#
# Example:
#   "sources/ed3d-plugins/plugins": [
#       "ed3d-basic-agents",
#       "ed3d-extending-claude",
#   ],
#
PLUGINS_MAPPING = {
    # ed3d-plugins
    "sources/ed3d-plugins/plugins": [
        "ed3d-basic-agents",
        "ed3d-extending-claude",
        "ed3d-house-style",
        "ed3d-plan-and-execute",
        "ed3d-playwright",
        "ed3d-research-agents",
        "ed3d-session-reflection",
    ],

    # learning-goal
    "sources/learning-goal": [
        "learning-goal",
    ],

    # learning-opportunities
    "sources/learning-opportunities": [
        "learning-opportunities",
        "learning-opportunities-auto",
        "orient",
    ],
}

# ============================================================================
# MARKETPLACE SOURCES - Source marketplace.json files to aggregate from
# ============================================================================
# Each entry is the path (relative to repo root) to a source marketplace.json.
# Only plugins that appear in PLUGINS_MAPPING will be included in the output.
#
MARKETPLACE_SOURCES = [
    "sources/ed3d-plugins/.claude-plugin/marketplace.json",
    "sources/learning-goal/.claude-plugin/marketplace.json",
    "sources/learning-opportunities/.claude-plugin/marketplace.json",
]

MARKETPLACE = {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": "clarizio-plugins",
        "version": "1.0.0",
        "description": "Marketplace for Christopher Clarizio's set of plugins",
        "owner": {
            "name": "Christopher Clarizio",
            "email": "christopher.a.clarizio@gmail.com"
        },
        "plugins": all_plugins,
    }


def get_plugins_to_copy(plugins_dir, plugin_filter):
    """Return the list of plugin names to copy from a directory.

    A valid plugin subdirectory must contain a .claude-plugin/plugin.json.
    """
    if not os.path.isdir(plugins_dir):
        return []

    available = [
        name for name in os.listdir(plugins_dir)
        if os.path.isdir(os.path.join(plugins_dir, name))
        and os.path.isfile(os.path.join(plugins_dir, name, ".claude-plugin", "plugin.json"))
    ]

    if plugin_filter == "*":
        return available
    elif isinstance(plugin_filter, list):
        return [p for p in plugin_filter if p in available]
    return []


def copy_plugin(src_path, dest_base_path, dry_run=False):
    """Copy a plugin directory to dest_base_path/<plugin_name>.

    Skips if the destination already exists.
    """
    plugin_name = os.path.basename(src_path)
    dest_path = os.path.join(dest_base_path, plugin_name)

    if os.path.exists(dest_path):
        print(f"  [SKIP] Already exists: {plugin_name}")
        return False, "exists"

    try:
        if not dry_run:
            shutil.copytree(src_path, dest_path, dirs_exist_ok=False)
        print(f"  [OK] Copied: {plugin_name}")
        return True, "copied"
    except Exception as e:
        print(f"  [FAIL] Error copying {plugin_name}: {e}")
        return False, "error"


def build_marketplace(repo_root, copied_plugin_names, dry_run=False):
    """Read source marketplace files and write a unified marketplace.json.

    Only includes plugins whose names appear in copied_plugin_names.
    Updates each plugin's source field to ./plugins/<plugin-name>.
    """
    all_plugins = []

    for rel_path in MARKETPLACE_SOURCES:
        marketplace_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(marketplace_path):
            print(f"[WARN] Marketplace source not found: {rel_path}")
            continue

        with open(marketplace_path, encoding="utf-8") as f:
            data = json.load(f)

        for entry in data.get("plugins", []):
            name = entry.get("name")
            if name in copied_plugin_names:
                updated = dict(entry)
                updated["source"] = f"./plugins/{name}"
                all_plugins.append(updated)

    marketplace = MARKETPLACE.set("plugins", all_plugins)

    out_dir = os.path.join(repo_root, "plugins", ".claude-plugin")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "marketplace.json")
    if not dry_run:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(marketplace, f, indent=4)
            f.write("\n")
    print(f"\n[OK] marketplace.json written with {len(all_plugins)} plugin(s)")
    return marketplace


def flatten_plugins(repo_root, dry_run=False):
    """Flatten all configured plugins and generate marketplace.json."""
    plugins_path = os.path.join(repo_root, "plugins")
    os.makedirs(plugins_path, exist_ok=True)

    mode = "(DRY RUN)" if dry_run else ""
    print(f"Flattening plugins from declarative mapping {mode}")
    print(f"Target directory: {plugins_path}\n")

    total = copied = skipped = failed = 0
    all_copied_names = set()

    for source_dir, plugin_filter in PLUGINS_MAPPING.items():
        source_path = os.path.join(repo_root, source_dir)

        if not os.path.isdir(source_path):
            print(f"[WARN] Source directory not found: {source_dir}")
            continue

        plugins_to_copy = get_plugins_to_copy(source_path, plugin_filter)

        if not plugins_to_copy:
            print(f"[INFO] No plugins to copy from: {source_dir}")
            continue

        print(f"Processing: {source_dir}")
        print(f"  Found {len(plugins_to_copy)} plugin(s): {', '.join(plugins_to_copy)}")

        for plugin_name in plugins_to_copy:
            plugin_src = os.path.join(source_path, plugin_name)
            total += 1
            success, status = copy_plugin(plugin_src, plugins_path, dry_run=dry_run)

            if status == "copied":
                copied += 1
                all_copied_names.add(plugin_name)
            elif status == "exists":
                skipped += 1
                all_copied_names.add(plugin_name)
            elif status == "error":
                failed += 1

        print()

    print("=" * 60)
    print(f"Plugin flattening complete:")
    print(f"  Total: {total}")
    print(f"  Copied: {copied}")
    print(f"  Skipped (already exist): {skipped}")
    print(f"  Failed: {failed}")

    build_marketplace(repo_root, all_copied_names, dry_run=dry_run)

    return failed == 0


if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if flatten_plugins(repo_root, dry_run=dry_run):
        sys.exit(0)
    else:
        sys.exit(1)
