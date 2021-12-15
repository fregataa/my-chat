from setuptools import find_packages, setup

install_requires = ['aiohttp>=3.6',
                    'aiohttp_jinja2',
                    'faker']


setup(name='chat',
      version='0.0.1',
      description='Chat example from aiohttp',
      platforms=['POSIX'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=install_requires,
      zip_safe=False)
