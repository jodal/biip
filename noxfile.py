"""Nox sessions."""

import nox

package = "biip"
locations = ["src", "tests", "noxfile.py", "docs/conf.py", "scripts"]

supported_pythons = ["3.8", "3.9", "3.10", "3.11"]
docs_python = "3.11"


@nox.session(python=supported_pythons)
def tests(session: nox.Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov", "--cov-report=xml"]
    session.run(
        "poetry",
        "install",
        "--quiet",
        "--all-extras",
        "--only=main,tests",
        external=True,
    )
    session.run("pytest", *args)


@nox.session(python=supported_pythons)
def black(session: nox.Session) -> None:
    """Check formatting using Black."""
    args = session.posargs or locations
    session.run(
        "poetry", "install", "--quiet", "--no-root", "--only=black", external=True
    )
    session.run("black", *args)


@nox.session(python=supported_pythons)
def ruff(session: nox.Session) -> None:
    """Lint using ruff."""
    args = session.posargs or locations
    session.run(
        "poetry", "install", "--quiet", "--no-root", "--only=ruff", external=True
    )
    session.run("ruff", *args)


@nox.session(python=supported_pythons)
def darglint(session: nox.Session) -> None:
    """Check docstrings using darglint."""
    args = session.posargs or ["src"]
    session.run(
        "poetry", "install", "--quiet", "--no-root", "--only=darglint", external=True
    )
    session.run("darglint", *args)


@nox.session(python=supported_pythons)
def mypy(session: nox.Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    session.run(
        "poetry",
        "install",
        "--quiet",
        "--all-extras",
        "--only=main,dev,docs,tests,mypy",
        external=True,
    )
    session.run("mypy", *args)


@nox.session(python=supported_pythons)
def pyright(session: nox.Session) -> None:
    """Type-check using pyright."""
    args = session.posargs or locations
    session.run(
        "poetry",
        "install",
        "--quiet",
        "--all-extras",
        "--only=main,dev,docs,tests,pyright",
        external=True,
    )
    session.run("pyright", *args)


@nox.session(python=docs_python)
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    session.run(
        "poetry",
        "install",
        "--quiet",
        "--all-extras",
        "--only=main,docs",
        external=True,
    )
    session.run("sphinx-build", "docs", "docs/_build")
