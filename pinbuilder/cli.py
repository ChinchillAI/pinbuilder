import typer
from pathlib import Path
from subprocess import run
from .svg.parser import parse

app = typer.Typer()


@app.command()
def list(path: Path):
    print(parse(path))


@app.command()
def test():
    cmd = "openscad --version"
    process = run(cmd.split(" "), capture_output=True)
    print(process.stdout.decode("ascii"))
    print(process.stderr.decode("ascii"))


if __name__ == "__main__":
    app()
