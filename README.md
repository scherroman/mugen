# mvgen

A music video generator based on beat patterns

Built with [essentia](https://github.com/MTG/essentia) and [moviepy](https://github.com/Zulko/moviepy)

## Installation (Mac OS X)

1 - [Install Miniconda](http://conda.pydata.org/miniconda.html) (A Python package manager)

2 - [Install Homebrew](http://brew.sh/) (General purpose package manager for mac)

3 - Install [tesseract](https://github.com/tesseract-ocr/tesseract)

`brew install tesseract --with-all-languages`

4 - Create mvgen virtual environment

`conda env create -f environment.yml`

5 - Activate mvgen environment

`source activate mvgen`

6 - Make sure most recent version of Xcode is installed

7 - [Install Essentia 2.1](http://essentia.upf.edu/documentation/installing.html) For OS X Via Homebrew 

8 - Move Essentia package from Homebrew to your mvgen conda environment

`cp -r /usr/local/lib/python2.7/site-packages/essentia /Users/myuser/miniconda/envs/mvgen/lib/python2.7/site-packages/essentia`

9 - [Fix matplotlib](http://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python)

10 - Download [scherroman/moviepy](https://github.com/scherroman/moviepy) from github (forked from [Zulko/moviepy](https://github.com/Zulko/moviepy) with added fix [#225](https://github.com/Zulko/moviepy/pull/225)).

11 - Install moviepy into mvgen conda environment (from downloaded moviepy directory)

`(sudo) python setup.py install`

## Examples

