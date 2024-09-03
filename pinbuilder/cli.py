import typer
from pathlib import Path
from subprocess import run
from .game import Game

app = typer.Typer()


@app.command()
def list(path: Path):
    _ = Game(path)


@app.command()
def generate(path: Path, out: Path | None = None):
    if out is None:
        out = Path("output")

    Game(path).generate(out)


@app.command()
def test():
    cmd = "openscad --version"
    process = run(cmd.split(" "), capture_output=True)
    print(process.stdout.decode("ascii"))
    print(process.stderr.decode("ascii"))


if __name__ == "__main__":
    app()
