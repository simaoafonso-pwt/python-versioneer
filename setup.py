#!/usr/bin/env python

import os, base64, tempfile, io
from pathlib import Path
from setuptools import setup, Command
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop

LONG = Path.read_text(Path(__file__).parent / "README.md")

# as nice as it'd be to versioneer ourselves, that sounds messy.
VERSION = "0.23.dev0"


def ver(s):
    return s.replace("@VERSIONEER-VERSION@", VERSION)

def get(fn, add_ver=False, unquote=False, do_strip=False, do_readme=False):
    with open(fn) as f:
        text = f.read()

    if add_ver:
        text = ver(text)
    if unquote:
        text = text.replace("%", "%%")
    if do_strip:
        text = "".join(line for line in text.splitlines(keepends=True)
                         if not line.endswith("# --STRIP DURING BUILD\n"))
    if do_readme:
        text = text.replace("@README@", get("README.md"))
    return text

def get_vcs_list():
    project_path = Path(__file__).absolute().parent / "src"
    return [filename
            for filename
            in os.listdir(str(project_path))
            if Path.is_dir(project_path / filename) and filename != "__pycache__"]

def generate_long_version_py(VCS):
    s = io.StringIO()
    s.write(get(f"src/{VCS}/long_header.py", add_ver=True, do_strip=True))
    for piece in ["src/subprocess_helper.py",
                  "src/from_parentdir.py",
                  f"src/{VCS}/from_keywords.py",
                  f"src/{VCS}/from_vcs.py",
                  "src/render.py",
                  f"src/{VCS}/long_get_versions.py"]:
        s.write(get(piece, unquote=True, do_strip=True))
    return s.getvalue()

def generate_versioneer_py():
    s = io.StringIO()
    s.write(get("src/header.py", add_ver=True, do_readme=True, do_strip=True))
    s.write(get("src/subprocess_helper.py", do_strip=True))

    for VCS in get_vcs_list():
        s.write(f"LONG_VERSION_PY['{VCS}'] = r'''\n")
        s.write(generate_long_version_py(VCS))
        s.write("'''\n")
        s.write("\n\n")

        s.write(get(f"src/{VCS}/from_keywords.py", do_strip=True))
        s.write(get(f"src/{VCS}/from_vcs.py", do_strip=True))

        s.write(get(f"src/{VCS}/install.py", do_strip=True))

    s.write(get("src/from_parentdir.py", do_strip=True))
    s.write(get("src/from_file.py", add_ver=True, do_strip=True))
    s.write(get("src/render.py", do_strip=True))
    s.write(get("src/get_versions.py", do_strip=True))
    s.write(get("src/cmdclass.py", do_strip=True))
    s.write(get("src/setupfunc.py", do_strip=True))

    return s.getvalue().encode("utf-8")


class make_versioneer(Command):
    description = "create standalone versioneer.py"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        with open("versioneer.py", "w") as f:
            f.write(generate_versioneer_py().decode("utf8"))
        return 0

class make_long_version_py_git(Command):
    description = "create standalone _version.py (for git)"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        assert os.path.exists("versioneer.py")
        long_version = generate_long_version_py("git")
        with open("git_version.py", "w") as f:
            f.write(long_version %
                    {"DOLLAR": "$",
                     "STYLE": "pep440",
                     "TAG_PREFIX": "tag-",
                     "PARENTDIR_PREFIX": "parentdir_prefix",
                     "VERSIONFILE_SOURCE": "versionfile_source",
                     })
        return 0

class my_build_py(build_py):
    def run(self):
        v = generate_versioneer_py()
        v_b64 = base64.b64encode(v).decode("ascii")
        lines = [v_b64[i:i+60] for i in range(0, len(v_b64), 60)]
        v_b64 = "\n".join(lines)+"\n"

        with open("src/installer.py") as f:
            s = f.read()
        s = ver(s.replace("@VERSIONEER-INSTALLER@", v_b64))

        with tempfile.TemporaryDirectory() as tempdir:
            installer = os.path.join(tempdir, "versioneer.py")
            with open(installer, "w") as f:
                f.write(s)

            self.py_modules = [os.path.splitext(os.path.basename(installer))[0]]
            self.package_dir.update({'': os.path.dirname(installer)})
            rc = build_py.run(self)
        return rc

# The structure of versioneer, with its components that are compiled into a single file,
# makes it unsuitable for development mode.
class develop(develop):
    def run(self):
        raise RuntimeError("Versioneer cannot be installed in developer/editable mode.")


setup(
    name = "versioneer",
    license = "CC0-1.0",
    version = VERSION,
    description = "Easy VCS-based management of project version strings",
    author = "Brian Warner",
    author_email = "warner-versioneer@lothar.com",
    url = "https://github.com/python-versioneer/python-versioneer",
    # "fake" is replaced with versioneer-installer in build_scripts. We need
    # a non-empty list to provoke "setup.py build" into making scripts,
    # otherwise it skips that step.
    py_modules = ["fake"],
    entry_points={
        'console_scripts': [
            'versioneer = versioneer:main',
        ],
    },
    long_description=LONG,
    long_description_content_type="text/markdown",
    cmdclass = { "build_py": my_build_py,
                 "make_versioneer": make_versioneer,
                 "make_long_version_py_git": make_long_version_py_git,
                 "develop": develop,
                 },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        ],
    )
