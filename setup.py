from setuptools import setup, find_packages

version = dict()
with open("mugen/version.py") as file:
    exec(file.read(), version)

optional_requirements = ['tesserocr==2.5.1']
tests_requirements = ['pytest==3.0.7', 'pytest-cov==2.4.0']

setup(
    name='mugen',
    version=version['__version__'],
    description='A music video generator based on rhythm',
    url='https://github.com/scherroman/mugen',
    author='Roman Scher',
    author_email='scher.roman@gmail.com',
    license='MIT',
    keywords='music-video amv montage remix rhythm video',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    install_requires=[
        'moviepy==0.2.3.5',
        "librosa==0.8.0",
        "Pillow==9.0.0",
        'numpy==1.21.0',
        'pysrt==1.1.1',
        'tqdm==4.11.2',
        'decorator==4.0.11',
        'dill==0.2.7.1',
        'requests==2.21.0',
        'imageio==2.4.1'
    ],
    extras_require={
        'full': optional_requirements,
        'tests': tests_requirements,
        'dev': optional_requirements + tests_requirements
    },
    entry_points={
        'console_scripts': [
            'mugen=scripts.cli:main'
        ]
    }
)
