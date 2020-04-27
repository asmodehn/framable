import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="framable",
    version="0.1.1",
    author="Asmodehn",
    author_email="asmodehn@gmail.com",
    description="Extending python classes with dataframe representation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asmodehn/framable",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
