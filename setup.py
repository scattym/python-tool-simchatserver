from setuptools import setup, find_packages

setup(
      name='simchatserver',
      version='2.30',
      description=('Project to communicate with simcom and meitrack devices'),
      url='https://bitbucket.org/mjclark1/python-tool-simchatserver.git',
      author='Matt Clark',
      author_email='mattjclark0407@hotmail.com',
      license='Copyright (C) Matthew Clark - All Rights Reserved',
      scripts=[
            'scripts/meitrackchatserver',
            'scripts/meitrackchatclient',
            'scripts/meitrackserver',
            'scripts/mqrecv-event',
            'scripts/mqrecv-cell-update',
            'scripts/mqrecv-gps-update',
            'scripts/mqrecv-firmware-update',
            'scripts/mqrecv-mt-file',
            'scripts/simchatserver',
            'scripts/simchatmaster',
            'scripts/simchatclient',
            'scripts/mqtt-receiver',
      ],
      packages=find_packages(),
      install_requires=[
            "pycrypto",
            "requests",
            "simplejson",
            "cachetools",
            "python-memcached",
            'pika',
            'geotooldbapi>=1.3',
            'geotoolapi>=1.8',
            'meitrackparser>=1.4',
            # 'geotool_api==1.0',
      ],
      # dependency_links=[
      #       "git+ssh://mjclark1@bitbucket.org/poslive/python-lib-geotool_api.git@1.0#egg=geotool_api-1.0"
      # ],
      zip_safe=False
)
