from setuptools import setup, find_packages

setup(
    name='f1dataexcel',
    version='1.0',
    packages=find_packages(), # Auto-discovers all subdirectories with __init__.py files and includes them in the package.
    entry_points={
        'console_scripts': [
            'mytool = mytool.__main__:main'
        ]
    },
)
