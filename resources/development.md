# SDK Development
If you are planning on contributing to the Skafos Python SDK, you must follow some basic guidelines to keep things
clean.

## Environment Requirements
While contributing to the Skafos Python SDK, you must have a Python 3.6
[conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
Use the one provided in `resources/skafossdk.yml`. Assuming you have a stable version of conda installed,
set up your development environment using the following commands:

```bash
conda env create -f skafossdk.yml
```

Activate the new environment and make sure it was properly installed:
```bash
conda activate skafossdk
conda list
```
Use this environment while working on the Skafos SDK.

## Dev Process

- First, do a fresh pull from the remote repository to make sure you have the most up-to-date changes.

#### **Minor Changes**
- If you are making a small change (non-breaking, minor addition/tweak), checkout a new branch with the name
of the current version (check `skafos/VERSION`) plus a **maintenance** version bump.
    - So if the current version is `0.1.2`, checkout a new branch with the name `0.1.3`. Check to make sure no one is
     working on that version in another branch somewhere.
    - Change the version number in the VERSION file to match.
- Test all changes/tweaks locally prior to any further steps.
- Open up a pull request on github, and request a review. Include thorough PR notes.
- After review, when you're ready to test with PyPI testing index, do the following:
    - Merge to master (which will kick off a drone build and deploy the sdk to a testing pypi index)
        - Under the hood it's doing `python setup.py sdist bdist_wheel` & `python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
        - It will automatically add a commit hash at the end of the version to differentiate on test.pypi
    - Pip install the uploaded `skafos` package. You can find the release history
    [here](https://test.pypi.org/project/skafos/#history). You will need to include the `--no-deps` flag on install.
- If testing succeeds, cut a release on github with a new tag,  


#### **Significant Changes**
- If you are making a medium to large change (non-breaking, new functionality, new feature),
checkout a new branch with the name of the current version (check `skafos/VERSION`) plus a **minor** version bump.
    - So if the current version is `0.1.2`, checkout a new branch with the name `0.2.0`. Check to make sure no one is
     working on that version in another branch somewhere.
    - Change the version number in the VERSION file to match.
- If you are making a large change that breaks backwards compatibility (incompatible API changes, major bug fix),
checkout a new branch with the name of the current version (check `skafos/VERSION`) plus a **major** version bump.
    - So if the current version is `0.1.2`, checkout a new branch with the name `1.0.0`. Check to make sure no one is
     working on that version in another branch somewhere.
    - Change the version number in the VERSION file to match.C
- Update the API urls in the `skafos/http.py` module to hit the Skafos staging env.
- You will treat this branch as a "staging" environment. Checkout another branch from here with the following naming
convention: `<feature|bug>/<your-initials>/<tiny-description>`.
- Begin development. Test changes locally prior to any further steps.
- Open up a **draft** pull request against the "staging" branch on github, and request a review. Include thorough PR notes.
- When you're ready to test with PyPI testing index, do the following:
    - Update the VERSION file with `.dev1` at the end of the current version.
    - Run: `python setup.py sdist bdist_wheel` from inside the `skafossdk/` dir.
        - This will create 2 build artifacts in the `dist/` dir to upload.
    - Run: `python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*` to upload to PyPI test.
        - You will need to enter valid PyPI credentials. If you do not have those, see the help section below.
    - Pip install the uploaded `skafos` package. You can find the release history
    [here](https://test.pypi.org/project/skafos/#history). You will need to include the `--no-deps` flag on install.
    - If testing succeeds, make final updates to the repo (reset version number back to base, change API urls)
    and commit/push. Take the PR out of draft state.
    - After PR has been reviewed and accepted, it will be merged to the staging branch.
    - Existing work on other branches stemmed from this branch will remain in progress, and should rebase to get the
    updates. The process above repeats until all work is in the staging branch. Final version changes are made and API
    urls are updated back to prod prior to PyPI release.

   ### **Important Notes**
   1. Documentation. You must do it! Any PR's that do not contain the necessary documentation in docstrings AND in
   `.rst` markdown (in the `docs/` dir) will not be accepted.
   2. Versioning. Familiarize yourself with
   [semantic versioning](https://packaging.python.org/guides/distributing-packages-using-setuptools/#id64)
   standards for Python. We use that.
   3. This document and process will evolve over time as things are flushed out! Stay tuned.


## Need help? Talk to these people:

1. [Tyler Hutcherson](mailto:tyler.hutcherson@skafos.ai)
2. [Griffin Walker](mailto:griffin.walker@skafos.ai)
