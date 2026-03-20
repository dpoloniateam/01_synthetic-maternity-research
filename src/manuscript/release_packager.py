"""
Release Packager
================
Assembles a complete, versioned release package of the synthetic maternity
research pipeline, including source code, data samples, evaluation results,
manuscript materials, supplementary files, configuration, and metadata.

NO LLM calls. All operations are file-system based.

Usage:
    python -m src.manuscript.release_packager --src src/ --data data/ --docs docs/ --output releases/
"""

import json
import argparse
import hashlib
import logging
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

from src.refinement.timestamped_run import TimestampedRun

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# STANDARD LIBRARY TO PIP PACKAGE MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

# Modules that are part of the Python standard library (no pip install needed)
STDLIB_MODULES = {
    "abc", "argparse", "ast", "asyncio", "base64", "bisect", "builtins",
    "calendar", "cgi", "cmd", "code", "codecs", "collections", "colorsys",
    "compileall", "concurrent", "configparser", "contextlib", "copy",
    "copyreg", "csv", "ctypes", "dataclasses", "datetime", "dbm", "decimal",
    "difflib", "dis", "distutils", "doctest", "email", "encodings", "enum",
    "errno", "faulthandler", "filecmp", "fileinput", "fnmatch", "fractions",
    "ftplib", "functools", "gc", "getopt", "getpass", "gettext", "glob",
    "grp", "gzip", "hashlib", "heapq", "hmac", "html", "http", "idlelib",
    "imaplib", "imghdr", "imp", "importlib", "inspect", "io", "ipaddress",
    "itertools", "json", "keyword", "lib2to3", "linecache", "locale",
    "logging", "lzma", "mailbox", "mailcap", "marshal", "math", "mimetypes",
    "mmap", "modulefinder", "multiprocessing", "netrc", "nis", "nntplib",
    "numbers", "operator", "optparse", "os", "ossaudiodev", "pathlib",
    "pdb", "pickle", "pickletools", "pipes", "pkgutil", "platform",
    "plistlib", "poplib", "posix", "posixpath", "pprint", "profile",
    "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue",
    "quopri", "random", "re", "readline", "reprlib", "resource", "rlcompleter",
    "runpy", "sched", "secrets", "select", "selectors", "shelve", "shlex",
    "shutil", "signal", "site", "smtpd", "smtplib", "sndhdr", "socket",
    "socketserver", "sqlite3", "sre_compile", "sre_constants", "sre_parse",
    "ssl", "stat", "statistics", "string", "stringprep", "struct",
    "subprocess", "sunau", "symtable", "sys", "sysconfig", "syslog",
    "tabnanny", "tarfile", "telnetlib", "tempfile", "termios", "test",
    "textwrap", "threading", "time", "timeit", "tkinter", "token",
    "tokenize", "trace", "traceback", "tracemalloc", "tty", "turtle",
    "turtledemo", "types", "typing", "unicodedata", "unittest", "urllib",
    "uu", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser",
    "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp",
    "zipfile", "zipimport", "zlib", "_thread",
}

# Mapping from import name to pip package name
IMPORT_TO_PIP = {
    "anthropic": "anthropic",
    "openai": "openai",
    "google": "google-generativeai",
    "genai": "google-generativeai",
    "dotenv": "python-dotenv",
    "numpy": "numpy",
    "np": "numpy",
    "scipy": "scipy",
    "pandas": "pandas",
    "pd": "pandas",
    "requests": "requests",
    "tqdm": "tqdm",
    "yaml": "pyyaml",
    "PIL": "pillow",
    "sklearn": "scikit-learn",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
    "tiktoken": "tiktoken",
    "transformers": "transformers",
    "datasets": "datasets",
    "huggingface_hub": "huggingface-hub",
}


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════


def sha256_file(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_tree_safe(src: str, dst: str):
    """Copy directory tree, creating destination if needed."""
    if os.path.exists(src):
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


def copy_file_safe(src: str, dst_dir: str, dst_name: str = None):
    """Copy a single file if it exists. Returns True if copied."""
    if os.path.exists(src):
        os.makedirs(dst_dir, exist_ok=True)
        dest = os.path.join(dst_dir, dst_name or os.path.basename(src))
        shutil.copy2(src, dest)
        return True
    return False


def _find_internal_packages(src_dir: str) -> set:
    """Find top-level package directories under src_dir (sibling modules)."""
    internal = set()
    parent = os.path.dirname(os.path.abspath(src_dir))
    if os.path.isdir(parent):
        for name in os.listdir(parent):
            pkg_path = os.path.join(parent, name)
            if os.path.isdir(pkg_path) and os.path.exists(os.path.join(pkg_path, "__init__.py")):
                internal.add(name)
    # Also add subdirectories of src_dir itself
    if os.path.isdir(src_dir):
        for name in os.listdir(src_dir):
            pkg_path = os.path.join(src_dir, name)
            if os.path.isdir(pkg_path):
                internal.add(name)
    return internal


def scan_imports(src_dir: str) -> set:
    """Scan all .py files under src_dir for import statements.
    Returns set of pip package names."""
    imports = set()
    import_pattern = re.compile(
        r"^(?:import|from)\s+([\w\.]+)"
    )

    for root, _dirs, files in os.walk(src_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath) as f:
                    for line in f:
                        line = line.strip()
                        m = import_pattern.match(line)
                        if m:
                            module = m.group(1).split(".")[0]
                            imports.add(module)
            except Exception:
                pass

    # Map to pip packages
    pip_packages = set()
    # Additional modules to skip (internal packages, special imports)
    skip_prefixes = {"src", "__", "test"}
    for mod in imports:
        if mod in STDLIB_MODULES:
            continue
        if any(mod.startswith(prefix) for prefix in skip_prefixes):
            continue
        if mod in IMPORT_TO_PIP:
            pip_packages.add(IMPORT_TO_PIP[mod])
        else:
            # Only include if it looks like a real third-party package
            # Skip anything that matches a known internal module directory
            internal_dirs = _find_internal_packages(src_dir)
            if mod not in internal_dirs:
                pip_packages.add(mod)

    return pip_packages


def scan_env_vars(src_dir: str) -> set:
    """Scan all .py files for environment variable references."""
    env_vars = set()
    patterns = [
        re.compile(r'os\.environ\.get\(\s*["\'](\w+)["\']'),
        re.compile(r'os\.environ\[\s*["\'](\w+)["\']'),
        re.compile(r'os\.getenv\(\s*["\'](\w+)["\']'),
    ]

    for root, _dirs, files in os.walk(src_dir):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath) as f:
                    content = f.read()
                for pattern in patterns:
                    for match in pattern.finditer(content):
                        env_vars.add(match.group(1))
            except Exception:
                pass

    return env_vars


def generate_checksums(release_dir: str) -> str:
    """Generate SHA-256 checksums for all files in the release directory."""
    lines = []
    for root, _dirs, files in sorted(os.walk(release_dir)):
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, release_dir)
            checksum = sha256_file(fpath)
            lines.append(f"{checksum}  {relpath}")
    return "\n".join(lines) + "\n"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════


def build_01_source_code(src_dir: str, release_dir: str):
    """01_Source_Code: copy entire src/ tree."""
    dest = os.path.join(release_dir, "01_Source_Code")
    log.info("Copying source code tree ...")
    copy_tree_safe(src_dir, dest)
    log.info("  -> %s", dest)


def build_02_data_samples(data_dir: str, release_dir: str):
    """02_Data_Samples: selected sample files."""
    dest = os.path.join(release_dir, "02_Data_Samples")
    os.makedirs(dest, exist_ok=True)

    # 5 sample personas
    composites_path = os.path.join(data_dir, "composite_personas", "composites.jsonl")
    if os.path.exists(composites_path):
        persona_dest = os.path.join(dest, "sample_personas.jsonl")
        with open(composites_path) as f_in, open(persona_dest, "w") as f_out:
            for i, line in enumerate(f_in):
                if i >= 5:
                    break
                f_out.write(line)
        log.info("  5 sample personas -> %s", persona_dest)

    # 3 sample transcripts
    transcripts_dir = os.path.join(data_dir, "transcripts")
    if os.path.isdir(transcripts_dir):
        sample_transcripts_dir = os.path.join(dest, "sample_transcripts")
        os.makedirs(sample_transcripts_dir, exist_ok=True)
        transcript_files = sorted([
            f for f in os.listdir(transcripts_dir)
            if f.startswith("T_S_") and f.endswith(".json")
        ])[:3]
        for tf in transcript_files:
            shutil.copy2(
                os.path.join(transcripts_dir, tf),
                os.path.join(sample_transcripts_dir, tf),
            )
        log.info("  %d sample transcripts -> %s", len(transcript_files), sample_transcripts_dir)

    # Final questionnaire
    for fname in ["FINAL_QUESTIONNAIRE.md", "FINAL_QUESTIONNAIRE.json"]:
        copy_file_safe(
            os.path.join(data_dir, "questionnaires", "final", fname),
            dest,
        )

    # Winner questionnaire (V4 refined)
    for fname in ["Q_V4_R1.json", "Q_V4_R1.md"]:
        src_path = os.path.join(data_dir, "questionnaires", "refined", fname)
        if not os.path.exists(src_path):
            # Fall back to final directory
            src_path = os.path.join(data_dir, "questionnaires", "final", fname)
        copy_file_safe(src_path, dest)

    log.info("  -> %s", dest)


def build_03_evaluation_results(data_dir: str, release_dir: str):
    """03_Evaluation_Results: key evaluation JSON files."""
    dest = os.path.join(release_dir, "03_Evaluation_Results")
    os.makedirs(dest, exist_ok=True)

    eval_dir = os.path.join(data_dir, "evaluation")

    # Key result files from evaluation/
    key_files = [
        ("version_ranking.json", eval_dir),
        ("dimension_heatmap.json", eval_dir),
        ("service_aggregate.json", eval_dir),
        ("inter_rater_agreement.json", eval_dir),
    ]
    for fname, parent in key_files:
        copy_file_safe(os.path.join(parent, fname), dest)

    # Saturation analysis
    sat_dir = os.path.join(eval_dir, "saturation")
    copy_file_safe(
        os.path.join(sat_dir, "saturation_analysis.json"), dest
    )

    # Robustness report
    adv_dir = os.path.join(eval_dir, "adversarial")
    copy_file_safe(
        os.path.join(adv_dir, "robustness_report.json"), dest
    )

    # Synthesis tables
    synth_dir = os.path.join(eval_dir, "synthesis")
    copy_file_safe(
        os.path.join(synth_dir, "paper_tables.json"), dest
    )

    log.info("  -> %s", dest)


def build_04_manuscript(docs_dir: str, release_dir: str):
    """04_Manuscript: copy docs/manuscript/ tree."""
    dest = os.path.join(release_dir, "04_Manuscript")
    manuscript_src = os.path.join(docs_dir, "manuscript")
    if os.path.isdir(manuscript_src):
        copy_tree_safe(manuscript_src, dest)
        log.info("  -> %s", dest)
    else:
        os.makedirs(dest, exist_ok=True)
        log.warning("  docs/manuscript/ not found; created empty directory")


def build_05_supplementary(docs_dir: str, release_dir: str):
    """05_Supplementary: copy docs/supplementary/ and docs/expert_evaluation/."""
    dest = os.path.join(release_dir, "05_Supplementary")
    os.makedirs(dest, exist_ok=True)

    supp_src = os.path.join(docs_dir, "supplementary")
    if os.path.isdir(supp_src):
        copy_tree_safe(supp_src, os.path.join(dest, "supplementary"))

    expert_src = os.path.join(docs_dir, "expert_evaluation")
    if os.path.isdir(expert_src):
        copy_tree_safe(expert_src, os.path.join(dest, "expert_evaluation"))

    log.info("  -> %s", dest)


def build_06_configuration(src_dir: str, data_dir: str, release_dir: str):
    """06_Configuration: models.py, plan files, .env.template."""
    dest = os.path.join(release_dir, "06_Configuration")
    os.makedirs(dest, exist_ok=True)

    # models.py
    copy_file_safe(
        os.path.join(src_dir, "config", "models.py"), dest
    )

    # Administration plan
    config_dir = os.path.join(data_dir, "config")
    copy_file_safe(
        os.path.join(config_dir, "administration_plan.json"), dest
    )

    # Refinement plan
    refinement_dir = os.path.join(data_dir, "refinement")
    copy_file_safe(
        os.path.join(refinement_dir, "refinement_plan.json"), dest
    )

    # .env.template (generated later, placeholder path)
    log.info("  -> %s", dest)


# ═══════════════════════════════════════════════════════════════════════════════
# RELEASE METADATA GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════


def generate_release_notes(
    data_dir: str, timestamp: str
) -> str:
    """Generate V2 release notes summarising the pipeline."""
    lines = [
        f"# V2 Stable Release Notes",
        f"",
        f"**Release timestamp:** {timestamp}",
        f"**Pipeline version:** V2 (Synthetic Maternity Research Pipeline)",
        f"",
        f"---",
        f"",
        f"## Pipeline Overview",
        f"",
        f"This release contains the complete output of a 7-sprint synthetic maternity",
        f"research pipeline that develops and validates a qualitative research instrument",
        f"for exploring maternity care experiences.",
        f"",
        f"### Sprint History",
        f"",
        f"| Sprint | Module | Description |",
        f"|--------|--------|-------------|",
        f"| 1 | Data Ingestion | Synthea EHR parser, FinePersonas filter, SNOMED registry |",
        f"| 2 | Persona Construction | 150 EHR-grounded composite personas with enriched narratives |",
        f"| 3 | Questionnaire Generation | 5 versioned instruments with EHR adaptation |",
        f"| 4 | Synthetic Interviews | 300 BIBD sessions with multi-provider persona rotation |",
        f"| 5 | Evaluation | 6-component quality assessment (richness, coverage, inter-rater, SERVQUAL) |",
        f"| 6 | Refinement | Blind spot analysis, probe enrichment, robustness testing, saturation |",
        f"| 7 | Manuscript & Release | Supplementary materials, expert evaluation, release packaging |",
        f"",
    ]

    # Try to add key metrics from methodology_log.json
    mlog_path = os.path.join(data_dir, "refinement", "methodology_log.json")
    if os.path.exists(mlog_path):
        with open(mlog_path) as f:
            mlog = json.load(f)

        lines.append("## Key Metrics")
        lines.append("")
        lines.append(f"- **Total pipeline iterations:** {mlog.get('total_pipeline_iterations', 'N/A')}")
        lines.append(f"- **Total interview sessions:** {mlog.get('total_sessions_run', 'N/A')}")
        lines.append(f"- **Total personas:** {mlog.get('total_personas_used', 'N/A')}")
        lines.append(f"- **Total pipeline cost:** ${mlog.get('total_cost_usd', 0):.4f} USD")
        lines.append(f"- **Robustness verdict:** {mlog.get('robustness_verdict', 'N/A')}")
        lines.append("")

        impact = mlog.get("refinement_impact", {})
        if impact:
            lines.append("## Refinement Impact")
            lines.append("")
            lines.append(f"- Richness improvement: +{impact.get('richness_improvement_pct', 0)}%")
            lines.append(f"- Surfacing rate improvement: +{impact.get('surfacing_rate_improvement_pct', 0)}%")
            lines.append(f"- Blind spots resolved: {impact.get('blind_spots_resolved', 0)}")
            lines.append(f"- Blind spots remaining: {impact.get('blind_spots_remaining', 0)}")
            lines.append("")

    lines.extend([
        "## Release Contents",
        "",
        "| Directory | Contents |",
        "|-----------|----------|",
        "| 01_Source_Code/ | Complete pipeline source code |",
        "| 02_Data_Samples/ | 5 sample personas, 3 sample transcripts, final questionnaire |",
        "| 03_Evaluation_Results/ | Version ranking, dimension heatmap, inter-rater, saturation |",
        "| 04_Manuscript/ | Tables, figures, results narrative |",
        "| 05_Supplementary/ | 6 appendices + expert evaluation materials |",
        "| 06_Configuration/ | Model config, administration plan, refinement plan |",
        "",
        "## Verification",
        "",
        "All files in this release are checksummed. Verify integrity with:",
        "",
        "```bash",
        "sha256sum -c SHA256_CHECKSUMS_*.txt",
        "```",
        "",
        "## Reproducibility",
        "",
        "To reproduce the pipeline:",
        "",
        "1. Install dependencies: `pip install -r requirements.txt`",
        "2. Configure environment variables (see `.env.template`)",
        "3. Run sprints 1-7 in sequence using the CLI commands documented",
        "   in each module's docstring",
        "",
    ])

    return "\n".join(lines)


def generate_requirements_txt(src_dir: str) -> str:
    """Scan source code and generate requirements.txt."""
    packages = scan_imports(src_dir)
    # Sort for deterministic output
    sorted_packages = sorted(packages)
    lines = [
        "# Requirements for Synthetic Maternity Research Pipeline",
        "# Auto-generated by release_packager.py",
        "#",
        "",
    ]
    for pkg in sorted_packages:
        lines.append(pkg)
    lines.append("")
    return "\n".join(lines)


def generate_env_template(src_dir: str) -> str:
    """Extract env var names from source code and generate .env.template."""
    env_vars = scan_env_vars(src_dir)
    sorted_vars = sorted(env_vars)
    lines = [
        "# Environment Variables for Synthetic Maternity Research Pipeline",
        "# Auto-generated by release_packager.py",
        "# Copy this file to .env and fill in your API keys",
        "#",
        "",
    ]
    for var in sorted_vars:
        lines.append(f"{var}=")
    lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════════


def package_release(
    src_dir: str, data_dir: str, docs_dir: str, output_dir: str
) -> dict:
    """Create a complete V2 stable release package."""
    run = TimestampedRun(output_dir)
    timestamp = run.timestamp

    release_name = f"V2_Stable_Release_{timestamp}"
    release_dir = os.path.join(output_dir, release_name)
    os.makedirs(release_dir, exist_ok=True)

    log.info("Creating release: %s", release_name)
    log.info("Release directory: %s", release_dir)

    # Build each section
    log.info("")
    log.info("--- 01_Source_Code ---")
    build_01_source_code(src_dir, release_dir)

    log.info("--- 02_Data_Samples ---")
    build_02_data_samples(data_dir, release_dir)

    log.info("--- 03_Evaluation_Results ---")
    build_03_evaluation_results(data_dir, release_dir)

    log.info("--- 04_Manuscript ---")
    build_04_manuscript(docs_dir, release_dir)

    log.info("--- 05_Supplementary ---")
    build_05_supplementary(docs_dir, release_dir)

    log.info("--- 06_Configuration ---")
    build_06_configuration(src_dir, data_dir, release_dir)

    # Generate .env.template
    log.info("")
    log.info("--- Generating .env.template ---")
    env_template = generate_env_template(src_dir)
    env_path = os.path.join(release_dir, "06_Configuration", ".env.template")
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    with open(env_path, "w") as f:
        f.write(env_template)
    run.files_written.append(env_path)
    log.info("  -> %s", env_path)

    # Generate requirements.txt
    log.info("--- Generating requirements.txt ---")
    req_content = generate_requirements_txt(src_dir)
    req_path = os.path.join(release_dir, "requirements.txt")
    with open(req_path, "w") as f:
        f.write(req_content)
    run.files_written.append(req_path)
    log.info("  -> %s", req_path)

    # Generate release notes
    log.info("--- Generating release notes ---")
    notes_content = generate_release_notes(data_dir, timestamp)
    notes_filename = f"V2_Release_Notes_{timestamp}.md"
    notes_path = os.path.join(release_dir, notes_filename)
    with open(notes_path, "w") as f:
        f.write(notes_content)
    run.files_written.append(notes_path)
    log.info("  -> %s", notes_path)

    # Generate SHA-256 checksums (must be last, after all files are written)
    log.info("--- Generating SHA-256 checksums ---")
    checksums_content = generate_checksums(release_dir)
    checksums_filename = f"SHA256_CHECKSUMS_{timestamp}.txt"
    checksums_path = os.path.join(release_dir, checksums_filename)
    with open(checksums_path, "w") as f:
        f.write(checksums_content)
    run.files_written.append(checksums_path)
    log.info("  -> %s", checksums_path)

    # Count files
    total_files = sum(
        len(files)
        for _, _, files in os.walk(release_dir)
    )

    # Write run manifest
    run.write_manifest("release_packager", config={
        "src_dir": src_dir,
        "data_dir": data_dir,
        "docs_dir": docs_dir,
        "output_dir": output_dir,
        "release_name": release_name,
        "total_files": total_files,
    })

    log.info("")
    log.info("=== Release Complete ===")
    log.info("  Release: %s", release_name)
    log.info("  Location: %s", release_dir)
    log.info("  Total files: %d", total_files)
    log.info("  Checksums: %s", checksums_path)
    log.info("  Release notes: %s", notes_path)

    return {
        "release_name": release_name,
        "release_dir": release_dir,
        "total_files": total_files,
        "notes_path": notes_path,
        "checksums_path": checksums_path,
        "requirements_path": req_path,
        "env_template_path": env_path,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Package a V2 stable release of the synthetic maternity pipeline."
    )
    parser.add_argument(
        "--src", default="src/",
        help="Path to source code directory (default: src/)"
    )
    parser.add_argument(
        "--data", default="data/",
        help="Path to data directory (default: data/)"
    )
    parser.add_argument(
        "--docs", default="docs/",
        help="Path to docs directory (default: docs/)"
    )
    parser.add_argument(
        "--output", default="releases/",
        help="Output directory for releases (default: releases/)"
    )

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    result = package_release(args.src, args.data, args.docs, args.output)

    log.info("")
    log.info("Release packaged successfully: %s", result["release_name"])


if __name__ == "__main__":
    main()
