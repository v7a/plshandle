import setuptools


with open("README.md", "r") as readme:
    setuptools.setup(
        name="plshandle",
        version="0.1",
        author="v7a",
        long_description=readme.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/v7a/plshandle",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
    )
