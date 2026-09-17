# -*- coding: utf-8 -*-
"""
Конвейер для папки контроллера в schemes_workspace:

    config.ini  ->  <name>.scheme.yaml  ->  <name>.svg  ->  <name>.pdf

  python tools/scheme_gen/build.py schemes_workspace/<Проект>/<контроллер>
  python tools/scheme_gen/build.py schemes_workspace/<Проект>          # все контроллеры проекта
  python tools/scheme_gen/build.py <папка> --force                    # пересоздать YAML из config.ini
  python tools/scheme_gen/build.py <папка> --no-pdf

YAML создаётся только если его ещё нет (или с --force): в нём живут ручные
правки — цвета проводов, артикулы, подписи. Если в папке есть готовый YAML,
шаг config.ini пропускается, генерируются только SVG и PDF.
"""

import sys
import os
import glob
import argparse
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FROM_CONFIG = os.path.join(HERE, "from_config.py")
GENERATE = os.path.join(HERE, "generate.py")


def build_dir(d, force, pdf):
    cfg = os.path.join(d, "config.ini")
    yamls = glob.glob(os.path.join(d, "*.scheme.yaml"))
    if os.path.exists(cfg) and (force or not yamls):
        cmd = [sys.executable, FROM_CONFIG, cfg] + (["--force"] if force else [])
        if subprocess.run(cmd).returncode:
            return False
        yamls = glob.glob(os.path.join(d, "*.scheme.yaml"))
    if not yamls:
        print(f"  ! {d}: нет ни config.ini, ни *.scheme.yaml — пропуск")
        return False
    ok = True
    for y in yamls:
        cmd = [sys.executable, GENERATE, y] + (["--pdf"] if pdf else [])
        ok &= subprocess.run(cmd).returncode == 0
    return ok


def main():
    ap = argparse.ArgumentParser(description="config.ini -> YAML -> SVG -> PDF")
    ap.add_argument("path", help="папка контроллера или папка проекта")
    ap.add_argument("--force", action="store_true", help="пересоздать YAML из config.ini")
    ap.add_argument("--no-pdf", action="store_true", help="не делать PDF")
    args = ap.parse_args()

    root = os.path.abspath(args.path)
    if os.path.exists(os.path.join(root, "config.ini")) or glob.glob(os.path.join(root, "*.scheme.yaml")):
        dirs = [root]
    else:
        dirs = sorted(p for p in glob.glob(os.path.join(root, "*"))
                      if os.path.isdir(p) and (os.path.exists(os.path.join(p, "config.ini"))
                                              or glob.glob(os.path.join(p, "*.scheme.yaml"))))
    if not dirs:
        sys.exit(f"В {root} не найдено папок контроллеров")
    ok = True
    for d in dirs:
        print(f"== {os.path.relpath(d)}")
        ok &= build_dir(d, args.force, not args.no_pdf)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):     # кириллица в консоли Windows
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    main()
