import nox


locations = ["src", "tests", "noxfile.py"]


@nox.session(python=["3.7", "3.8"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python="3.8")
def flake8(session):
    args = session.posargs or locations
    session.install(
        "flake8", "flake8-black", "flake8-bugbear", "flake8-import-order"
    )
    session.run("flake8", *args)


@nox.session(python="3.8")
def mypy(session):
    args = session.posargs or locations
    session.install("mypy")
    session.run("mypy", *args)
