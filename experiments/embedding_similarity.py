from rich import print
from rich.traceback import install
install()

print("[bold green]Success![/bold green]")
print("[bold red]Error:[/bold red] something went wrong")
print({"source": "lab.pdf", "page": 1, "text": "EECE 2311 ..."})
