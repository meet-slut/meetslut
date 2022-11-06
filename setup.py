import setuptools

# with open("README.md", "r", encoding="utf-8") as fhand:
#     long_description = fhand.read()

long_description = "hello"
setuptools.setup(
    name="meetslut",
    version="0.1",
    author="Maze",
    author_email="3257575985@qq.com",
    description=("An amazing package to download pictures form internet."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meet-slut/meetslut",
    project_urls={
        "Bug Tracker": "https://github.com/meet-slut/meetslut/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "beautifulsoup4"],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "meetslut = meetslut.cli:main",
        ]
    }
)