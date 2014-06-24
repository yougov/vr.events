import setuptools

with open('README.txt') as readme:
    long_description = readme.read()
with open('CHANGES.txt') as changes:
    long_description += '\n\n' + changes.read()

setup_params = dict(
    name='vr.events',
    version='1.1.2',
    author="YouGov, Plc.",
    author_email="dev@yougov.com",
    description="vr.events",
    long_description=long_description,
    url="https://bitbucket.org/yougov/vr.events",
    packages=setuptools.find_packages(),
    namespace_packages=['vr'],
    install_requires=[
        'vr.common',
        'six',
        'redis',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'mock',
    ],
)

if __name__ == '__main__':
    setuptools.setup(**setup_params)
