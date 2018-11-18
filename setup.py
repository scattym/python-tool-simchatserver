from setuptools import setup, find_packages

setup(
      name='simchatserver',
      version='2.87.dev0',
      description='Project to communicate with simcom and meitrack devices',
      url='https://bitbucket.org/mjclark1/python-tool-simchatserver.git',
      author='Matt Clark',
      author_email='mattjclark0407@hotmail.com',
      license='Copyright (C) Matthew Clark - All Rights Reserved',
      scripts=[
            'scripts/meitrackchatserver',
            'scripts/meitrackbot',
            'scripts/meitrackchatclient',
            'scripts/meitrackserver',
            'scripts/mqrecv-cell-update',
            'scripts/mqrecv-debug-log',
            'scripts/mqrecv-event',
            'scripts/mqrecv-firmware-update',
            'scripts/mqrecv-gps-update',
            'scripts/mqrecv-mt-file',
            'scripts/simchatserver',
            'scripts/simchatmaster',
            'scripts/simchatclient',
            'scripts/mqtt-receiver',
            'scripts/firmware-upload',
      ],
      packages=find_packages(),
      install_requires=[
            "pycryptodome",
            "requests",
            "simplejson",
            "cachetools",
            "python-memcached",
            'pika',
            'aio_pika',
            'geotooldbapi>=2.1',
            'geotoolapi>=1.23',
            'meitrackparser>=2.3',
            'celery[sqs]',
            'kombu',
            # 'geotool_api==1.0',
      ],
      # dependency_links=[
      #       "git+ssh://mjclark1@bitbucket.org/poslive/python-lib-geotool_api.git@1.0#egg=geotool_api-1.0"
      # ],
      zip_safe=False
)
