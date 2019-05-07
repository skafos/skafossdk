import os
import setuptools


def read(fname):
  """Utility function to read the README and VERSION files."""
  return open(os.path.join(os.path.dirname(__file__), fname)).read()


with open('requirements.txt', 'r') as r:
    REQS = r.read().splitlines()


setuptools.setup(
  name="skafos",
  packages=setuptools.find_packages(),
  version=read('skafos/VERSION'),
  license="Apache Software License",
  description="Python wrapper for loading, fetching, and listing model versions with the Skafos platform.",
  long_description=read('README.md'),
  long_description_content_type="text/markdown",
  author="Skafos, LLC",
  author_email="skafos@skafos.ai",
  url="https://github.com/skafos/skafossdk",
  download_url='',
  keywords=['machine learning delivery', 'mobile deployment', 'model versioning'],
  install_requires=REQS,
  include_package_data=True,
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3'
  ],
  project_urls={
    "Source": "https://github.com/skafos/skafossdk",
    "Website": "https://skafos.ai"
  },
  python_requires=">=3"
)
