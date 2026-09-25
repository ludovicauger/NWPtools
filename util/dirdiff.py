#!/usr/bin/env python3
"""
Compare deux arborescences de répertoires.

- Liste les fichiers présents dans un seul des deux répertoires.
- Pour les fichiers présents des deux côtés et différents, lance
  `git diff --no-index --word-diff`.
- Pour les namelists Fortran (nom de fichier commençant ou finissant par "nam"),
  les deux fichiers sont d'abord normalisés dans des copies temporaires :
  groupes (&NAME ... /) triés par ordre alphabétique, puis variables triées
  à l'intérieur de chaque groupe. Les fichiers d'origine ne sont jamais modifiés.

Usage : dirdiff.py DIR1 DIR2 [-x MOTIF ...] [--no-sort]
"""
import argparse
import filecmp
import fnmatch
import os
import re
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# Parsing / tri de namelist
# ---------------------------------------------------------------------------

GROUP_START = re.compile(r'^\s*[&$]([A-Za-z_]\w*)', re.I)
GROUP_END_WORD = re.compile(r'^[&$]end\b', re.I)
# Nom de variable juste avant un '=' : NAME, NAME(1:3), A%B(2), ...
KEY_BEFORE_EQ = re.compile(
    r'([A-Za-z_]\w*(?:\s*\([^()]*\))?(?:\s*%\s*[A-Za-z_]\w*(?:\s*\([^()]*\))?)*)\s*$'
)


def strip_comment(line):
    """Retire un commentaire '!' situé hors chaîne de caractères."""
    quote = None
    for i, c in enumerate(line):
        if quote:
            if c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c == '!':
            return line[:i]
    return line


def find_group_end(text):
    """Position du '/' (ou &end) terminant le groupe hors chaîne, sinon -1.
    Retourne (debut_marqueur, fin_marqueur)."""
    quote = None
    i = 0
    while i < len(text):
        c = text[i]
        if quote:
            if c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c == '/':
            return i, i + 1
        elif c in '&$':
            m = GROUP_END_WORD.match(text[i:])
            if m:
                return i, i + m.end()
        i += 1
    return -1, -1


def normalize_value(value):
    """Met la valeur sur une ligne, sans espaces autour des virgules
    (hors chaînes) et sans virgule finale."""
    parts = re.split(r"""('[^']*'|"[^"]*")""", value)
    for i in range(0, len(parts), 2):          # indices pairs = hors chaîne
        p = ' '.join(parts[i].split())
        parts[i] = re.sub(r'\s*,\s*', ',', p)
    return ''.join(parts).strip().rstrip(',').strip()


def split_assignments(body):
    """Découpe le corps d'un groupe en liste de (clé, valeur)."""
    eq_pos = []
    quote = None
    depth = 0
    for i, c in enumerate(body):
        if quote:
            if c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c == '(':
            depth += 1
        elif c == ')':
            depth = max(0, depth - 1)
        elif c == '=' and depth == 0:
            eq_pos.append(i)

    items = []
    key_starts = []
    for p in eq_pos:
        m = KEY_BEFORE_EQ.search(body[:p])
        key_starts.append(m.start() if m else p)

    leading = body[:key_starts[0]].strip(' \t\n,') if eq_pos else body.strip(' \t\n,')
    for k, p in enumerate(eq_pos):
        key = re.sub(r'\s+', '', body[key_starts[k]:p])
        end = key_starts[k + 1] if k + 1 < len(eq_pos) else len(body)
        value = body[p + 1:end]
        value = normalize_value(value)
        items.append((key, value))
    return leading, items


def natural_key(s):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s.upper())]


def sort_namelist(text):
    """Renvoie le texte de la namelist avec groupes et variables triés."""
    lines = [strip_comment(l) for l in text.splitlines()]
    flat = '\n'.join(lines)

    groups = []      # (nom, [(clé, valeur)], texte_non_parsé)
    outside = []     # texte hors groupe (conservé en tête)
    pos = 0
    while pos < len(flat):
        m = re.search(r'(?m)^\s*[&$]([A-Za-z_]\w*)', flat[pos:])
        if not m:
            rest = flat[pos:].strip()
            if rest:
                outside.append(rest)
            break
        before = flat[pos:pos + m.start()].strip()
        if before:
            outside.append(before)
        name = m.group(1)
        start_body = pos + m.end()
        if name.lower() == 'end':      # &end orphelin
            pos = start_body
            continue
        s, e = find_group_end(flat[start_body:])
        if s < 0:
            body, pos = flat[start_body:], len(flat)
        else:
            body, pos = flat[start_body:start_body + s], start_body + e
        leading, items = split_assignments(body)
        items.sort(key=lambda kv: natural_key(kv[0]))
        groups.append((name, items, leading))

    groups.sort(key=lambda g: g[0].upper())

    out = []
    for o in outside:
        out.append(o)
    for name, items, leading in groups:
        out.append('&' + name)
        if leading:
            out.append('  ' + leading)
        for k, v in items:
            out.append(f'  {k}={v},')
        out.append('/')
    return '\n'.join(out) + '\n'


def is_namelist(path):
    b = os.path.basename(path).lower()
    return b.startswith('nam') or b.endswith('nam')


# ---------------------------------------------------------------------------
# Parcours et comparaison
# ---------------------------------------------------------------------------

def list_files(root, excludes):
    files = set()
    for d, dirs, fnames in os.walk(root):
        dirs[:] = sorted(x for x in dirs
                         if not any(fnmatch.fnmatch(x, p) for p in excludes))
        for f in fnames:
            if any(fnmatch.fnmatch(f, p) for p in excludes):
                continue
            files.add(os.path.relpath(os.path.join(d, f), root))
    return files


def git_diff(a, b, cwd=None):
    cmd = ['git', '--no-pager', 'diff', '--no-index', '--word-diff']
    if sys.stdout.isatty():
        cmd.append('--color=always')
    cmd += ['--', a, b]
    sys.stdout.flush()
    subprocess.run(cmd, cwd=cwd)
    sys.stdout.flush()


def read_text(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dir1')
    ap.add_argument('dir2')
    ap.add_argument('-x', '--exclude', action='append', default=['.git'],
                    help='motif (fnmatch) de fichier/répertoire à ignorer '
                         '(répétable, .git ignoré par défaut)')
    ap.add_argument('--no-sort', action='store_true',
                    help='ne pas trier les namelists avant le diff')
    args = ap.parse_args()

    for d in (args.dir1, args.dir2):
        if not os.path.isdir(d):
            sys.exit(f'Erreur : {d} n\'est pas un répertoire')

    f1 = list_files(args.dir1, args.exclude)
    f2 = list_files(args.dir2, args.exclude)

    only1 = sorted(f1 - f2)
    only2 = sorted(f2 - f1)
    common = sorted(f1 & f2)

    print(f'### Fichiers uniquement dans {args.dir1} : {len(only1)}')
    for f in only1:
        print(f'  - {f}')
    print(f'\n### Fichiers uniquement dans {args.dir2} : {len(only2)}')
    for f in only2:
        print(f'  + {f}')

    n_diff = n_nam_same = 0
    print(f'\n### Fichiers communs différents')
    with tempfile.TemporaryDirectory(prefix='dirdiff_') as tmp:
        for rel in common:
            p1 = os.path.join(args.dir1, rel)
            p2 = os.path.join(args.dir2, rel)
            if filecmp.cmp(p1, p2, shallow=False):
                continue

            if is_namelist(rel) and not args.no_sort:
                s1 = sort_namelist(read_text(p1))
                s2 = sort_namelist(read_text(p2))
                if s1 == s2:
                    n_nam_same += 1
                    print(f'\n=== {rel} : namelist identique après tri')
                    continue
                n_diff += 1
                print(f'\n=== {rel} (namelist triée)')
                for side, content in (('A', s1), ('B', s2)):
                    t = os.path.join(tmp, side, rel)
                    os.makedirs(os.path.dirname(t), exist_ok=True)
                    with open(t, 'w') as f:
                        f.write(content)
                git_diff(os.path.join('A', rel), os.path.join('B', rel), cwd=tmp)
            else:
                n_diff += 1
                print(f'\n=== {rel}')
                git_diff(p1, p2)

    print(f'\n### Résumé : {len(only1)} seulement dans {args.dir1}, '
          f'{len(only2)} seulement dans {args.dir2}, '
          f'{len(common)} communs dont {n_diff} différents'
          f' (+{n_nam_same} namelists identiques après tri)')


if __name__ == '__main__':
    main()
