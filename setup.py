from setuptools import setup

setup(
    name='cloud_computing',
    packages=['cloud_computing'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-security',
        'flask-admin',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
