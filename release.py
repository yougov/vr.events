"""
vr.events may be released using 'jaraco.packaging.release'. To make a release,
install jaraco.packaging and run 'python -m jaraco.packaging.release'
"""

files_with_versions = 'setup.py',

post_release_bump = lambda ver: ver
