try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='pipedly',
      version='0.1',
      description='Piping service Apis to build new services',
      author='Abhishek Nath',
      author_email='illidan.elf@gmail.com',
      url='https://github.com/abhisheknath666/PipedlyRecruit',
      platforms = ['Any'],
      py_modules = ['lib.scrapinghub.scrapinghub'],
      install_requires = ['requests','django','MySQL-python']
      )
