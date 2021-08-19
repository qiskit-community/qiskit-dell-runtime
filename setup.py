import os

from setuptools import find_packages, setup

here = os.path.dirname(os.path.realpath(__file__))
readme_path = os.path.join(here, "README.md")
requirements_path = os.path.join(here, "requirements.txt")
test_requirements_path = os.path.join(here, "requirements-test.txt")
with open(readme_path, "r") as _fp:
    long_description = _fp.read()

with open(requirements_path) as _fp:
    REQUIREMENTS = _fp.readlines()

with open(test_requirements_path) as _fp:
    TEST_REQUIREMENTS = _fp.readlines()

setup(
    name="qiskit_dell",
    version="0.0.1",
    author="DellTechnologies",
    author_email="v.fong@dell.com",
    packages=find_packages(exclude=["*test*"]),
    description="Qiskit provider for Runtime Emulator backends",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering",
    ],
    keywords="qiskit sdk quantum",
    python_requires=">=3.6",
    setup_requires=["pytest-runner"],
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    zip_safe=False,
    include_package_data=True,
)
