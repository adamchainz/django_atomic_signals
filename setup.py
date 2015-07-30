#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


packages = [
    'django_atomic_signals',
]

requires = [
    'Django>=1.6.0,<1.8',
]

tests_require = [
    'flake8',
    'django-nose',
]

setup(
    name='django-atomic-signals',
    version='1.1.0',
    description='Signals for atomic transaction blocks in Django 1.6+',
    author='Nick Bruun',
    author_email='nick@bruun.co',
    url='http://bruun.co/',
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
