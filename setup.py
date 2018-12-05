import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ecs",
    version="0.0.1",
    author="avikor",
    author_email="44028161+avikor@users.noreply.github.com",
    description="An Entity–Component–System (ECS) framework for writing games with pygame.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avikor/ecs",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
