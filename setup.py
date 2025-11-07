import setuptools
from setuptools.command.install import install
import subprocess
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Get the current git commit hash
        try:
            commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
            # Define the config directory and version file path
            config_dir = os.path.join(os.path.expanduser("~"), ".config", "ymp")
            version_file = os.path.join(config_dir, "version.txt")
            # Create the directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            # Write the commit hash to the version file
            with open(version_file, "w") as f:
                f.write(commit_hash)
        except Exception as e:
            print(f"Could not save git commit hash: {e}")


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ymp",
    version="0.5.1",
    author="pheinze",
    author_email="pheinze82@gmail.com",
    description="A command-line music player for YouTube.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pheinze/ymp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
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
        'setuptools',
        'textual',
    ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['ymp = ymp.__main__:main']
    },
    cmdclass={
        'install': PostInstallCommand,
    },
)
