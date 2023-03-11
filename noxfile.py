"""Nox sessions."""

import nox

package = "biip"
locations = ["src", "tests", "noxfile.py", "docs/conf.py"]


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", "--all-extras", "--only=main,tests", external=True)
    session.run("pytest", *args)


@nox.session(python="3.11")
def coverage(session: nox.Session) -> None:
    """Upload test coverage data."""
    session.run("poetry", "install", "--no-root", "--only=tests", external=True)
    session.run("coverage", "xml", "--fail-under=0")
    session.run("codecov", *session.posargs)


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def black(session: nox.Session) -> None:
    """Check formatting using Black."""
    args = session.posargs or locations
    session.run("poetry", "install", "--no-root", "--only=black", external=True)
    session.run("black", *args)


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def ruff(session: nox.Session) -> None:
    """Lint using ruff."""
    args = session.posargs or locations
    session.run("poetry", "install", "--no-root", "--only=ruff", external=True)
    session.run("ruff", *args)


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def darglint(session: nox.Session) -> None:
    """Check docstrings using darglint."""
    args = session.posargs or ["src"]
    session.run("poetry", "install", "--no-root", "--only=darglint", external=True)
    session.run("darglint", *args)


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.run("poetry", "install", "--only=mypy", external=True)
    session.run("mypy", *args)


@nox.session(python="3.11")
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    session.run("poetry", "install", "--all-extras", "--only=main,docs", external=True)
    session.run("sphinx-build", "docs", "docs/_build")
