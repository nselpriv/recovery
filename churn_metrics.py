import subprocess
import re
from collections import defaultdict
import matplotlib.pyplot as plt
from file_utils import module_name_from_file_path
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_churn(code_root_folder, since_date):
    
    code_root_folder = Path(code_root_folder)
    if not (code_root_folder / ".git").exists():
        logger.error(f"'{code_root_folder}' is not a git repository.")
        return {}

    cmd = [
        'git',
        'log',
        f'--since={since_date}',
        '--numstat',
        '--pretty=format:',
    ]
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=code_root_folder,
            text=True,
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logger.error(f"Error running git command: {stderr}")
            return {}
    except Exception as e:
        logger.error(f"Failed to execute git command: {e}")
        return {}

    lines = stdout.strip().split('\n')
    logger.debug(f"Raw git log output lines: {len(lines)}")
    py_lines = [line for line in lines if line.strip() and line.split()[-1].endswith('.py')]
    logger.debug(f"Filtered .py lines: {len(py_lines)}")

    if not py_lines:
        logger.warning(f"No .py files found in git log since {since_date}.")
        return {}

    churn_data = defaultdict(lambda: {'added': 0, 'deleted': 0, 'commits': 0})
    current_file = None

    for line in py_lines:
        match = re.match(r'(\d+)\s+(\d+)\s+(.+)', line.strip())
        if match:
            added, deleted, file_path = match.groups()
            current_file = file_path
            churn_data[current_file]['added'] += int(added)
            churn_data[current_file]['deleted'] += int(deleted)
            churn_data[current_file]['commits'] += 1
        else:
            logger.debug(f"Skipping malformed line: {line}")
            current_file = None

    excluded_dirs = {"_pyinstaller", "tools", "doc", "benchmarks", "ci", "wheels", "swig"}

    module_churn = defaultdict(lambda: {'added': 0, 'deleted': 0, 'commits': 0})
    for file_path, stats in churn_data.items():
        module = module_name_from_file_path(file_path, code_root_folder, strict=False, excluded_dirs=excluded_dirs)
        if module is not None:
            module_churn[module]['added'] += stats['added']
            module_churn[module]['deleted'] += stats['deleted']
            module_churn[module]['commits'] += stats['commits']
        else:
            logger.debug(f"Skipped file '{file_path}' in module_churn (no valid module name).")

    for module, stats in module_churn.items():
        total_churn = stats['added'] + stats['deleted']
        logger.info(f"Module: {module}")
        logger.info(f"  Added: {stats['added']}, Deleted: {stats['deleted']}, Total Churn: {total_churn}")
        logger.info(f"  Commits: {stats['commits']}")
        logger.info(f"  Churn Density: {total_churn / stats['commits'] if stats['commits'] > 0 else 0}")

    top_churn = sorted(
        module_churn.items(),
        key=lambda x: x[1]['added'] + x[1]['deleted'],
        reverse=True
    )[:5]
    logger.info("\nTop 5 Modules by Churn:")
    for module, stats in top_churn:
        logger.info(f"{module}: {stats['added'] + stats['deleted']} lines")

    Path("./img").mkdir(exist_ok=True)

    if top_churn:
        modules, churns = zip(*[(m, s['added'] + s['deleted']) for m, s in top_churn])
        plt.figure(figsize=(10, 5))
        plt.bar(modules, churns, color='skyblue')
        plt.xticks(rotation=45, ha='right', fontsize=8)
        plt.xlabel('Modules')
        plt.ylabel('Total Churn (Lines Added + Deleted)')
        plt.title(f"Top 5 Modules by Churn (Since {since_date})")
        plt.tight_layout()
        plt.savefig("./img/churn_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
    else:
        logger.warning("No modules with churn data to plot.")

    return module_churn