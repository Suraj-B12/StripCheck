"""Package source and the built website without local data or credentials.

Run from any directory: python scripts/package_release.py [output.zip]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.venv', 'venv', 'node_modules', '.build', '.swiftpm', '__pycache__',
            '.pytest_cache', '.mypy_cache', '.ruff_cache', '.vite', '.idea', '.vscode',
            'xcuserdata', 'data', 'runs', 'dist-pages', '.claude', '.codex', '.agents', '.aws', '.config'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', type=Path, default=ROOT.parent / 'StripCheck-Web-iOS.zip')
    args = parser.parse_args()
    if not (ROOT / 'web/dist/index.html').is_file():
        parser.error('Build the website first: npm --prefix web run build')
    archive_path = args.output.resolve()
    files = []
    for current, directories, names in os.walk(ROOT):
        directories[:] = [d for d in directories if d not in EXCLUDED and not (
            d == 'build' and Path(current).relative_to(ROOT).parts and
            Path(current).relative_to(ROOT).parts[0] in {'paper', 'ios'})]
        for name in names:
            path = Path(current) / name
            if path.is_symlink() or path.resolve() == archive_path:
                continue
            if name in {'.DS_Store', '__preview.html'} or name.endswith((
                '.pyc', '.tsbuildinfo', '.xcuserstate', '.db', '.db-wal', '.db-shm',
                '.sqlite', '.sqlite3', '.zip', '.bundle')):
                continue
            if name.startswith('.env') and name != '.env.example':
                continue
            files.append((path.relative_to(ROOT).as_posix(), path))
    files.sort()
    manifest = {'format': 1, 'files': {name: hashlib.sha256(path.read_bytes()).hexdigest()
                                      for name, path in files}}
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive_path, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in files:
            archive.write(path, 'StripCheck/' + name)
        archive.writestr('StripCheck/DELIVERY-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    with ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        for name, digest in manifest['files'].items():
            assert hashlib.sha256(archive.read('StripCheck/' + name)).hexdigest() == digest
        for name in archive.namelist():
            assert not any(part in EXCLUDED for part in Path(name).parts)
    print(json.dumps({'archive': str(archive_path), 'files': len(files) + 1,
                      'bytes': archive_path.stat().st_size,
                      'sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest()}, indent=2))


if __name__ == '__main__':
    main()
