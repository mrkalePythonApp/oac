# -*- coding: utf-8 -*-
'''Setup function for the package.'''

from setuptools import setup, find_namespace_packages

setup(
    name='oac',
    description='OpenAPI 3 CLI utilities',
    long_description='Set of utilities for processing OpenAPI 3 documents.',
    long_description_content_type='text/plain',
    version='0.5.0',
    author='Libor Gabaj',
    author_email='libor.gabaj@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
    ],
    keywords='OpenAPI, OAS, OAS3',
    url='http://github.com/mrkalePythonApp/oac',
    license='MIT',
    install_requires=['click', 'pyyaml', 'tabulate'],
    packages=find_namespace_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'oac = src.oac:oac',
            'oac_bundle = src.oac:oac_bundle',
            'oac_orphans = src.oac:oac_orphans',
            'oac_paths = src.oac:oac_paths',
            'oac_prune = src.oac:oac_prune',
            'oac_convert = src.oac:oac_convert',
        ],
    },
    zip_safe=False
)
