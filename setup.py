import os
import setuptools


def read(fname):
    """Utility function to read the README and VERSION files."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read().strip('\n')

with open('requirements.txt', 'r') as r:
    REQS = r.read().splitlines()

if "VERSION" in os.environ:
    VERSION = os.environ["VERSION"]
else:
    if "BUILD_NUMBER" in os.environ:
        VERSION = read("skafos/VERSION") + ".dev" + os.environ["BUILD_NUMBER"]
    else:
        VERSION = read("skafos/VERSION")

setuptools.setup(
  name="skafos",
  packages=setuptools.find_packages(),
  version=VERSION,
  license="Apache Software License",
  description="Python wrapper for loading, fetching, and listing model versions with the Skafos platform.",
  long_description=read("README.md"),
  long_description_content_type="text/markdown",
  author="Skafos, LLC",
  author_email="skafos@skafos.ai",
  url="https://github.com/skafos/skafossdk",
  download_url='',
  keywords=["machine learning delivery", "mobile deployment", "model versioning"],
  install_requires=REQS,
  include_package_data=True,
  tests_require=["pytest"],
  setup_requires=["pytest-runner"],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3'
  ],
  project_urls={
    "Dashboard": "https://dashboard.skafos.ai",
    "SDK Documentation": "https://sdk.skafos.ai",
    "Source": "https://github.com/skafos/skafossdk",
    "Website": "https://skafos.ai"
  },
  python_requires=">=3"
)
