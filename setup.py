from setuptools import setup, find_packages

setup(name='simchatserver',
      version='0.1.dev0',
      description=('Project to communicate with simcom devices'),
      url='https://bitbucket.org/mjclark1/python-tool-simchatserver.git',
      author='Matt Clark',
      author_email='mattjclark0407@hotmail.com',
      license='Copyright (C) Matthew Clark - All Rights Reserved',
      scripts=['scripts/simchatserver'],
      packages=find_packages(),
      install_requires=[
      ],
      zip_safe=False)
