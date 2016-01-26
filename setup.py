#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


packages = [
    'django_atomic_signals',
]

requires = [
]

tests_require = [
    'flake8',
    'django-nose',
]

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='django-atomic-signals',
    version='2.0.0',
    description='Signals for atomic transaction blocks in Django 1.6+',
    long_description=readme,
    author='Nick Bruun',
    author_email='nick@bruun.co',
    maintainer='Adam Johnson',
    maintainer_email='me@adamj.eu',
    url='https://github.com/adamchainz/django_atomic_signals',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'django_atomic_signals': 'django_atomic_signals'},
    include_package_data=True,
    tests_require=tests_require,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=True,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)
