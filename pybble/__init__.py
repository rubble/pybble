"""The python API to the Rubble programming language over REST

.. moduleauthor:: Emlyn Clay <emlyn@viditeck.com>

"""
version = '0.1.6'

setup_params = {
  'name': 'pybble',
  'packages': ['pybble'],
  'version': version,
  'description': """A python API to the Rubble programming
                 language over HTTP using the Rubble REST API.""",
  'url': 'https://github.com/viditeck/pybble',
  'download_url': 'https://github.com/viditeck/pybble/tarball/%s' % version,
  'keywords': ['rubble', 'logic language', 'api'],
  'author': 'Emlyn Clay',
  'author_email': 'emlyn@rubble.tech',
  'license': 'MIT',
  'install_requires': ["requests"]
}