from setuptools import find_packages, setup, Command

with open("wrapper/__version__.py", "r") as f:
    exec(f.read())

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
    install_requires=[
        'passlib',
        'Flask_SocketIO',
        'Flask',
        'storify',
        'msgpack',
        'psutil',
        'future',
        'waitress',
        'importlib_resources',
        'nbt',
        'humanize',
        'requests',
    ],
)
