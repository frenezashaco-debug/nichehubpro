"""Run-local validated text checkpoints and bounded publication retries."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def checkpoint_path(root, keyword, category):
    identity = hashlib.sha256((keyword + '\0' + category).encode()).hexdigest()
    return Path(root) / '.publication-state' / (identity + '.json')


def load_checkpoint(root, keyword, category, validate):
    path = checkpoint_path(root, keyword, category)
    try:
        record = json.loads(path.read_text(encoding='utf-8'))
        data = record['article']
        if (record['keyword'] != keyword or record['category'] != category
                or not isinstance(data, dict) or data.get('category') != category
                or validate(data)):
            return None
        return data
    except (OSError, ValueError, KeyError, TypeError):
        return None


def save_checkpoint(root, keyword, category, data):
    path = checkpoint_path(root, keyword, category)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'keyword': keyword, 'category': category,
                                    'article': data}, ensure_ascii=False), encoding='utf-8')
    os.replace(temporary, path)


def run_with_retries(command, run=subprocess.run, sleep=time.sleep, attempts=3):
    """The command fixes the day once, so retries cannot advance the plan."""
    for attempt in range(attempts):
        print(f'Publication attempt {attempt + 1}/{attempts}', flush=True)
        try:
            result = run(command, timeout=1000)
            if result.returncode == 0:
                return 0
        except subprocess.TimeoutExpired:
            print('Publication attempt timed out.', flush=True)
        if attempt + 1 < attempts:
            sleep(30 * (attempt + 1))
    return 1


def main():
    import batch_24weeks as batch
    if not batch.AUTO_PUBLISH:
        raise RuntimeError('Automatic publication mode is required.')
    # The plan's legacy loader treats malformed JSON as an empty catalog.
    # Refuse that state instead of accidentally choosing an already published day.
    import re
    registry = (Path(batch.BASE_DIR) / 'articles.js').read_text(encoding='utf-8')
    match = re.search(r'const ARTICLES = (\[[\s\S]*?\]);', registry)
    if not match:
        raise RuntimeError('Article registry missing; refusing to select a publication day.')
    catalog = json.loads(match.group(1))
    if not isinstance(catalog, list) or any(
            not isinstance(item, dict) or not isinstance(item.get('slug'), str) for item in catalog):
        raise RuntimeError('Article registry invalid; refusing to select a publication day.')
    published = batch.load_published()
    entry = next((item for item in batch.PLAN if item[0] not in published), None)
    if entry is None:
        print('Publication plan complete.')
        return 0
    root = Path(__file__).resolve().parent
    command = [sys.executable, '-u', str(root / 'batch_24weeks.py'), '--day', str(entry[0])]
    print(f'Pinned publication day: {entry[0]}', flush=True)
    return run_with_retries(command)


if __name__ == '__main__':
    sys.exit(main())
