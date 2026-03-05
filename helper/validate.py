import lief
import sys
import click
from colorama import Fore


def validate(app1, app2):
    pe1 = lief.parse(app1)
    pe2 = lief.parse(app2)
    
    if pe1 is None:
        click.echo(Fore.RED + f"Error: {app1} is not a valid binary")
        return False
    if pe2 is None:
        click.echo(Fore.RED + f"Error: {app2} is not a valid binary")
        return False
    
    if pe1.format != lief.Binary.FORMATS.PE:
        click.echo(Fore.RED + f"Error: {app1} is not a PE file")
        return False
    if pe2.format != lief.Binary.FORMATS.PE:
        click.echo(Fore.RED + f"Error: {app2} is not a PE file")
        return False

    if pe1.header.machine != pe2.header.machine:
        click.echo(Fore.RED + f"Error: architecture mismatch ({pe1.header.machine} vs {pe2.header.machine})")
        return False
    if pe1.optional_header.magic != pe2.optional_header.magic:
        click.echo(Fore.RED + f"Error: bitness mismatch ({pe1.optional_header.magic} vs {pe2.optional_header.magic})")
        return False
    
    if lief.PE.Header.CHARACTERISTICS.DLL in pe1.header.characteristics_list:
        click.echo(Fore.RED + f"Error: {app1} is a DLL not an executable")
        return False
    if lief.PE.Header.CHARACTERISTICS.DLL in pe2.header.characteristics_list:
        click.echo(Fore.RED + f"Error: {app2} is a DLL not an executable")
        return False
    
    # If no errors, return
    click.echo(Fore.GREEN + f"\nFiles are valid")
    return True