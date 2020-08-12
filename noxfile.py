"""Nox sessions."""

import nox


package = "biip"
locations = ["src", "tests", "noxfile.py", "docs/conf.py"]


@nox.session(python=["3.7", "3.8"])
def tests(session):
    """Run the test suite."""
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python=["3.7", "3.8"])
def flake8(session):
    """Lint using flake8."""
    args = session.posargs or locations
    session.install(
        "darglint",
        "flake8",
        "flake8-annotations",
        "flake8-black",
        "flake8-bugbear",
        "flake8-docstrings",
        "flake8-import-order",
    )
    session.run("flake8", *args)


@nox.session(python=["3.7", "3.8"])
def mypy(session):
    """Type-check using mypy."""
    args = session.posargs or locations
    session.install("mypy")
    session.run("mypy", *args)


@nox.session(python="3.8")
def docs(session):
    """Build the documentation."""
    session.run("poetry", "install", "--no-dev", external=True)
    session.install("sphinx", "sphinx_rtd_theme", "sphinx-autodoc-typehints")
    session.run("sphinx-build", "docs", "docs/_build")


@nox.session(python="3.8")
def coverage(session):
    """Upload test coverage data."""
    session.install("coverage[toml]", "codecov")
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)
