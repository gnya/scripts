import functools
import os
import re


def _cmp_version(a, b):
    for i in range(max(len(a), len(b))):
        v_a = a[i] if i < len(a) else 0
        v_b = b[i] if i < len(b) else 0

        if v_a > v_b:
            return 1

        if v_a < v_b:
            return -1

    return 0


def find_latest_asset(blend_dir):
    files = []

    for f in os.listdir(blend_dir):
        if re.match(r'^[A-Z]+_(?!.*test).*\.blend$', f):
            version = []

            for s in f.split('_'):
                if m := re.search(r'[vt]?(\d+)', s):
                    version.append(int(m.group(1)))

            files.append((f, version))

    key = functools.cmp_to_key(lambda a, b: _cmp_version(a[1], b[1]))
    files = sorted(files, key=key)

    return os.path.join(blend_dir, files[-1][0]), files[-1][0]
