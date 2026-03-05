import click
import os
import lief
from helper.validate import validate
from helper.inject import inject
from helper.verification import verify
from colorama import Fore
# disable lief error loggin
lief.logging.disable()

@click.command()
@click.argument('app1',
                type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),
                required=True)
@click.argument('app2',
                type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),
                required=True)

def fuse(app1, app2):
    
    ok = validate(app1, app2)
    if not ok:
        return
    
    pe = inject(app1, app2)

    output_name = os.path.join(os.path.dirname(app1), "fused_" + os.path.basename(app1))
    pe.write(output_name)

    click.echo(Fore.BLUE + f"\n-> {os.path.basename(app2)} fused into {os.path.basename(app1)}\n")

    click.echo(Fore.RESET + "Verifying fused app:\n")
    verify(output_name, app1, app2)

if __name__ == "__main__":
    fuse()