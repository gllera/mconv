import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mconv", # Replace with your own username
    version="1.0.0",
    author="Gabriel Llera",
    author_email="g113r4@gmail.com",
    description="Multimedia library maintainer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gllera/mconv",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
