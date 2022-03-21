from setuptools import find_packages, setup

version = dict()
with open("mugen/version.py") as file:
    exec(file.read(), version)

test_requirements = ["pytest==7.0.0", "pytest-cov==3.0.0", "pytest-xdist==2.5.0"]
development_requirements = [
    "black==22.1.0",
    "isort==5.10.1",
    "flake8==4.0.1",
    "pre-commit==2.17.0",
]

setup(
    name="mugen",
    version=version["__version__"],
    description="A music video generator based on rhythm",
    url="https://github.com/scherroman/mugen",
    author="Roman Scher",
    author_email="scher.roman@gmail.com",
    license="MIT",
    keywords="music-video amv montage remix rhythm video",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Programming Language :: Python",
    ],
    packages=find_packages(),
    install_requires=[
        "moviepy==1.0.3",
        "librosa==0.8.1",
        "Pillow==9.0.1",
        "numpy==1.22.2",
        "pysrt==1.1.1",
        "tqdm==4.62.3",
        "decorator==4.0.11",
        "dill==0.3.4",
        "proglog==0.1.9",
        "pytesseract==0.3.8",
    ],
    extras_require={
        "tests": test_requirements,
        "development": test_requirements + development_requirements,
    },
    entry_points={"console_scripts": ["mugen=scripts.cli:main"]},
)
