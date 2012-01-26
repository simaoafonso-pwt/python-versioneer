#### START
# This file helps to compute a version number in source trees obtained from
# git-archive tarball (such as those provided by githubs download-from-tag
# feature). Distribution tarballs (build by setup.py sdist) and build
# directories (produced by setup.py build) will contain a much shorter file
# that just contains the computed version number.

# This file is released into the public domain. Generated by versioneer-0.5
# (https://github.com/warner/python-versioneer)

# these strings will be replaced by git during git-archive
git_refnames = "%(DOLLAR)sFormat:%%d%(DOLLAR)s"
git_full = "%(DOLLAR)sFormat:%%H%(DOLLAR)s"

#### SUBPROCESS_HELPER
#### MIDDLE
#### PARENTDIR

tag_prefix = "%(TAG_PREFIX)s"
parentdir_prefix = "%(PARENTDIR_PREFIX)s"
versionfile_source = "%(VERSIONFILE_SOURCE)s"

def get_versions():
    variables = { "refnames": git_refnames, "full": git_full }
    ver = versions_from_expanded_variables(variables, tag_prefix)
    if not ver:
        ver = versions_from_vcs(tag_prefix, versionfile_source)
    if not ver:
        ver = versions_from_parentdir(parentdir_prefix, versionfile_source)
    if not ver:
        ver = {"version": "unknown", "full": ""}
    return ver

#### END

