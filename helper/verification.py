import lief
import click
import os
from colorama import Fore

def verify(output_path, app1, app2):
    pe = lief.parse(output_path)

    if pe is None:
        click.echo(Fore.RED + "Output is not a valid PE")
        return False
    click.echo(Fore.GREEN + "Valid PE structure")

    # Check if .fused section exists in the fused app
    fused_section = pe.get_section(".fused")
    if fused_section is None:
        click.echo(Fore.RED + ".fused section not found")
        return False
    click.echo(Fore.GREEN + f".fused section found at {hex(fused_section.virtual_address)}")

    # Check if markers are in correct places
    content = bytes(fused_section.content)
    m1 = content.find(b"FUSED__START__1")
    m2 = content.find(b"FUSED__START__2")
    m3 = content.find(b"FUSED__END_____")

    if m1 == -1 or m2 == -1 or m3 == -1:
        click.echo(Fore.RED + "Markers not found")
        return False
    if not (m1 < m2 < m3):
        click.echo(Fore.RED + "Markers in wrong order")
        return False
    click.echo("Markers in correct order")

    #check if sizes make sense
    app1_size = os.path.getsize(app1)
    app2_size = os.path.getsize(app2)
    click.echo(Fore.YELLOW + f"{os.path.basename(app1)} embedded: {m2 - m1 - 15} bytes (expected {app1_size})")
    click.echo(Fore.YELLOW + f"{os.path.basename(app2)} embedded: {m3 - m2 - 15} bytes (expected {app2_size})")

    click.echo(Fore.BLUE + "\n-> Verification passed")
    return True


    