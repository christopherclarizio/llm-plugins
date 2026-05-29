#!/usr/bin/env python3
"""
Flatten skills from sources subtrees into the skills directory.

This script recursively finds all skill directories within sources subdirectories
and copies them into the main skills directory.
"""

import os
import shutil
import sys
from pathlib import Path


def find_skill_directories(base_path):
    """Find all directories that appear to be skill directories.

    A skill directory is identified as a directory that:
    - Is named as a skill (lowercase with hyphens)
    - Contains skill-like files (.md, .json, etc.)
    - Is within a 'skills' subdirectory
    """
    skill_dirs = []

    for root, dirs, files in os.walk(base_path):
        # Look for directories within 'skills' subdirectories
        if 'skills' in root:
            skills_dir = os.path.join(root, 'skills')
            if os.path.isdir(skills_dir):
                # Found a skills directory, get all subdirectories in it
                for item in os.listdir(skills_dir):
                    item_path = os.path.join(skills_dir, item)
                    if os.path.isdir(item_path):
                        skill_dirs.append(item_path)

    return skill_dirs


def copy_skill(src_path, dest_base_path):
    """Copy a skill directory to the destination.

    Handles naming conflicts by appending a suffix.
    """
    skill_name = os.path.basename(src_path)
    dest_path = os.path.join(dest_base_path, skill_name)

    # Handle conflicts
    if os.path.exists(dest_path):
        counter = 1
        base_name = skill_name
        while os.path.exists(dest_path):
            skill_name = f"{base_name}_{counter}"
            dest_path = os.path.join(dest_base_path, skill_name)
            counter += 1
        print(f"  Name conflict detected. Copying as: {skill_name}")

    try:
        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        print(f"  [OK] Copied: {skill_name}")
        return True
    except Exception as e:
        print(f"  [FAIL] Error copying {skill_name}: {e}")
        return False


def flatten_skills(repo_root):
    """Main function to flatten all skills."""
    sources_path = os.path.join(repo_root, 'sources')
    skills_path = os.path.join(repo_root, 'skills')

    if not os.path.isdir(sources_path):
        print(f"Error: sources directory not found at {sources_path}")
        return False

    # Create skills directory if it doesn't exist
    os.makedirs(skills_path, exist_ok=True)

    print(f"Flattening skills from: {sources_path}")
    print(f"Target directory: {skills_path}\n")

    # Find all skill directories
    skill_dirs = find_skill_directories(sources_path)

    if not skill_dirs:
        print("No skill directories found.")
        return False

    print(f"Found {len(skill_dirs)} skill directory/directories:\n")

    # Copy each skill
    successful = 0
    for skill_dir in skill_dirs:
        relative_path = os.path.relpath(skill_dir, sources_path)
        print(f"Processing: {relative_path}")
        if copy_skill(skill_dir, skills_path):
            successful += 1

    print(f"\n{'='*60}")
    print(f"Flattening complete: {successful}/{len(skill_dirs)} skills copied")
    return True


if __name__ == '__main__':
    # Get the repository root (directory containing this script)
    repo_root = os.path.dirname(os.path.abspath(__file__))

    if flatten_skills(repo_root):
        sys.exit(0)
    else:
        sys.exit(1)
