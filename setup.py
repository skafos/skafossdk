import setuptools

with open('README.md', 'r') as d:
    DESCRIPTION = d.read()

with open('skafos/VERSION', 'r') as v:
    VERSION = v.read().strip()

with open('requirements.txt', 'r') as r:
    REQS = r.read().splitlines()

setuptools.setup(
  name="skafos",
  packages=setuptools.find_packages(),
  version=VERSION,
  license="Apache Software License",
  description="Python wrapper for loading, fetching, and listing model versions with the Skafos platform.",
  long_description=DESCRIPTION,
  long_description_content_type="text/markdown",
  author="Skafos, LLC",
  author_email="skafos@skafos.ai",
  url="https://github.com/skafos/skafossdk",
  download_url='',
  keywords=['machine learning delivery', 'mobile deployment', 'model versioning'],
  install_requires=REQS,
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3'
  ],
  project_urls={
    "SDK Documentation": "",
    "Skafos Platform Documentation": "",
    "Source": "https://github.com/skafos/skafossdk",
    "Website": "https://skafos.ai"
  },
  python_requires=">=3"
)
