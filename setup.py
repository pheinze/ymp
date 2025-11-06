import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ymp",
    version="0.5.0",
    author="pheinze",
    author_email="pheinze82@gmail.com",
    description="Your Music Player for the console.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pheinze/ymp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'yt_dlp',
        'pyfiglet',
        'requests',
        'pydub',
        'termcolor',
        'beautifulsoup4',
        'colorama',
        'lxml',
        'simpleaudio',
        'rich',
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['ymp = ymp.__main__:main']
    },
)
