import setuptools

from plshandle import __version__


with open("README.md", "r") as readme:
    setuptools.setup(
        name="plshandle",
        version=__version__,
        author="v7a",
        long_description=readme.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/v7a/plshandle",
        keywords=["exception", "contract", "error handling"],
        install_requires=["mypy >= 0.750", "setuptools >= 41.0", "toml >= 0.10",],
        package_data={"plshandle": ["py.typed"]},
        packages=setuptools.find_namespace_packages(
            exclude=("plshandle.tests", "plshandle.tests.*", "doc", "doc.*")
        ),
        project_urls={
            "Documentation": "https://plshandle.readthedocs.io",
            "Source": "https://github.com/v7a/plshandle",
            "Tracker": "https://github.com/v7a/plshandle/issues",
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3 :: Only",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Quality Assurance",
            "Topic :: Software Development :: Testing",
        ],
    )
