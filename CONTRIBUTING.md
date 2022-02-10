How to contribute
=====================================

<p align="center">
    <img src="https://github.com/prise-3d/behavioral-online-experiment/blob/master/docs/source/_static/behavioral_logo.svg" alt="" width="60%">
</p>



# Welcome !

Thank you for taking the time to read this guide for the package's contribution. I'm glad to know that you may bring a lot to the behavioral online experiment framework. This document will show you the good development practices used in the project and how you can easily participate in its evolution!

# Table of contents

1. [Submission processes](#submission-process)

    1.1. [Submit an issue](#submit-an-issue)

    1.2. [Pull request](#pull-request)

    1.3. [Seek support](#seek-support)

2. [Coding conventions](#coding-conventions)

    2.1. [Python conventions](#python-conventions)

    2.2. [Code documentation](#code-documentation)

    2.3. [Testing](#test-implementation)


# Submission process

## Submit an issue

Do not hesitate to report bug or issue in [https://github.com/prise-3d/behavioral-online-experiment/issues](https://github.com/prise-3d/behavioral-online-experiment/issues) with the common template header:

```
**Framework version:** X.X.X (see documentation)
**Issue label:** XXXXX
**Targeted modules:** `......`, `.....`
**Operating System:** Manjaro Linux

**Description:** XXXXX
```

## Pull request

If you have made changes to the project you have forked, you can submit a pull request in [https://github.com/prise-3d/behavioral-online-experiment/pulls](https://github.com/prise-3d/behavioral-online-experiment/pulls) in order to have your changes added inside new version of the `Macop` package. A [GitHub documentation](https://help.github.com/articles/about-pull-requests/) about pull requests is available if necessary.

To enhance the package, do not hesitate to fix bug or missing feature. To do that, just submit your pull request with this common template header:

```
**Framework version:** X.X.X
**Enhancements label:** XXXXX
**Targeted modules:** `.......`, `.......`
**New modules:** `.......`, `........`

**Description:** XXXXX
```

**Note:** the code conventions required for the approval of your changes are described below.

Whatever the problem reported, I will thank you for your contribution to this project. So do not hesitate.

## Seek support

If you have any problem with the use of the package, issue or pull request submission, do not hesitate to let a message to [https://github.com/prise-3d/behavioral-online-experiment/discussions](https://github.com/prise-3d/behavioral-online-experiment/discussions). Especially in the question and answer section. 

You can also contact me at the following email address: `contact@jeromebuisine.fr`.

# Coding conventions

## Python conventions

This project follows the [coding conventions](http://google.github.io/styleguide/pyguide.html) implemented by Google. To help you to format **\*.py** files, it is possible to use the [yapf](https://github.com/google/yapf/) Python package developed by Google.

```
yapf -ir -vv experiments
```

**Note:** you need at least Python version >=3.7.0.

## Package modules conventions

As you perhaps already saw, package contains multiples modules and submodules. It's really import to be well organized package and let it intuitive to access as possible to features.

You can refer to the [documentation](https://prise-3d.github.io/behavioral-online-experiment) if necessary.

In order to facilitate the integration of new modules, do not hesitate to let me know the name it could have beforehand in your pull request.

## Code documentation

You can generate documentation and display updates using these following commands:

```
cd docs
make clean && make html
firefox _build/html/index.html
```
