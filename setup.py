from setuptools import setup, find_packages

setup(
    name='ShadowSearch',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'appdirs',
        'requests',
        'pandas'
    ],
    entry_points={
        'console_scripts': [
            'shvsch = shadowsearch:run_cli',
        ]
    }
)
