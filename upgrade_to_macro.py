import os
import re
import argparse

# Gates we care about
GATES = ["X180", "X90", "mX90", "Y90", "mY90", "Y180"]
gate_alt = "|".join(GATES)

# Regex to match:
#  play("GATE", qe[, *amp(...)][, t])
pattern = re.compile(
    rf'''play\(\s*
        (?P<quote>['"])(?P<gate>{gate_alt})(?P=quote)      # "GATE"
        (?:\s*\*\s*(?P<amp>amp\([^)]*\)))?                  # *amp(...)
        \s*,\s*(?P<qe>\w+)                                  # , qe
        (?:\s*,\s*(?P<t>[^)\s]+))?                          # , t (optional)
        \s*\)
    ''',
    re.VERBOSE
)

def transform_line(line):
    def repl(m):
        gate = m.group("gate")
        qe   = m.group("qe")
        amp  = m.group("amp")
        t    = m.group("t")

        args = [qe]
        if amp:
            args.append(f"a={amp}")
        if t:
            args.append(f"t={t}")

        return f"play_{gate}({', '.join(args)})"

    return pattern.sub(repl, line)

def process_file(path, inplace=True):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = [transform_line(l) for l in lines]

    if inplace and new_lines != lines:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Updated: {path}")

def main(root_dir, dry_run):
    for dirpath, _, files in os.walk(root_dir):
        for fname in files:
            if fname.endswith('.py'):
                full = os.path.join(dirpath, fname)
                if dry_run:
                    with open(full, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if pattern.search(line):
                                print(f"[DRY] {full}:{i}: {line.strip()}")
                else:
                    process_file(full)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Refactor play(\"GATE\"[, *amp(...)][, t]) → play_GATE(qe[, a=...][, t=...])"
    )
    p.add_argument("root", help="Project root directory")
    p.add_argument("--dry-run", action="store_true",
                   help="Show matches without modifying files")
    args = p.parse_args()
    main(args.root, args.dry_run)
