"""Request a branch-based Pages build and wait for this exact commit."""
import os
import subprocess
import time

import requests


def wait_for_build(session, base, sha, attempts=60, sleep=time.sleep):
    response = session.post(base + '/builds', timeout=30)
    response.raise_for_status()
    for _ in range(attempts):
        response = session.get(base + '/builds/latest', timeout=30)
        response.raise_for_status()
        build = response.json()
        if build.get('commit') == sha:
            if build.get('status') == 'built':
                print('GitHub Pages deployed commit ' + sha)
                return
            if build.get('status') == 'errored':
                raise RuntimeError('GitHub Pages build failed; inspect the Pages build log.')
        sleep(15)
    raise RuntimeError('Timed out waiting for the publication commit to deploy.')


def main():
    base = 'https://api.github.com/repos/' + os.environ['GITHUB_REPOSITORY'] + '/pages'
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    session = requests.Session()
    session.headers.update({'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                            'Accept': 'application/vnd.github+json'})
    response = session.get(base, timeout=30)
    response.raise_for_status()
    settings = response.json()
    if settings.get('build_type', 'legacy') != 'legacy':
        raise RuntimeError('Pages uses a custom workflow; run its deployment before distribution.')
    if settings.get('source', {}).get('branch') != 'main':
        raise RuntimeError('Pages source is not main; refusing to build the wrong branch.')
    wait_for_build(session, base, sha)


if __name__ == '__main__':
    main()
