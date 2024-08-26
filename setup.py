from setuptools import setup, find_packages

setup(
    name='create_kapp',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'create-kapp=create_kapp.create_kapp:main',
        ],
    },
)
