from setuptools import setup

setup(name='pybble',
      packages=['pybble'],
      version='0.1',
      description="""A python API to the Rubble programming
                     language over HTTP using the Rubble REST API.""",
      url='https://github.com/viditeck/pybble',
      download_url='https://github.com/viditeck/pybble/tarball/0.1',
      keywords = ['rubble', 'logic language', 'api'],
      author='Emlyn Clay',
      author_email='emlyn@viditeck.com',
      license='MIT',
      install_requires=["requests"],
      )
