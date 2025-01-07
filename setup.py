from setuptools import find_packages, setup, Command

with open("wrapper/__version__.py", "r") as f:
    exec(f.read())

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='Wrapper.py',
    version=__version__,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    license='MIT',
    long_description=open('README.md').read(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'mcwrapper=wrapper.wrapper:main',  # Adjust the import path as necessary
        ],
    },
    install_requires=install_requires
)
