from setuptools import setup

setup(name='pybble',
      version='0.2',
      description="""A python API to the Rubble programming
                     language over HTTP using the Rubble REST API.""",
      url='http://github.com/emlync/pybble',
      author='Emlyn Clay',
      author_email='emlyn@viditeck.com',
      license='MIT',
      packages=['pybble'],
      install_requires=["requests"],
      )
