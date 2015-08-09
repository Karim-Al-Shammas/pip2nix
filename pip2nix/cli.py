import click
from .config import Config


@click.group()
def cli():
    pass


@cli.command()
@click.option('--build', '-b', type=click.Path(), metavar='<dir>',
              help="Directory to unpack packages and build in.")
@click.option('--download', '-d', type=click.Path(), metavar='<dir>',
              help="Directory to download packages to.")
@click.option('--pre/--no-pre',
              help="Also look for pre-release and unstable versions.")
@click.option('--output', metavar='<path>',
              help="Write the generated nix to <path>.")

@click.option('--index-url', '-i', metavar='<url>',
              default='https://pypi.python.org/simple',
              help="Base URL of Python Package Index.")
@click.option('--extra-index-url', metavar='<url>',
              help="Extra index URLs to use.")
@click.option('--no-index',
              help="Ignore indexes.")
@click.option('--find-links', '-f', metavar='<url>',
              help="Path or url to a package listing/directory.")

#TODO:
# --allow-external <package>  Allow the installation of a package even if it is externally hosted
# --allow-all-external        Allow the installation of all packages that are externally hosted
# --allow-unverified <package>
# Allow the installation of a package even if it is hosted in an insecure and unverifiable way
# --process-dependency-links  Enable the processing of dependency links.

@click.option('--configuration', metavar='<path>',
              help="Read pip2nix configuration from <path>.")

@click.option('--editable', '-e', multiple=True, type=click.Path(),
              metavar='<spec>',
              help="Add a requirement specifier (for pip install compatibility).")
@click.option('--requirement', '-r', multiple=True, type=click.Path(),
              metavar='<file>',
              help="Load specifiers from a requirements file.")
@click.argument('specifiers', nargs=-1)
def generate(specifiers, **kwargs):
    """Generate a .nix file with specified packages."""
    kwargs['specifiers'] = specifiers

    config = Config()
    config.merge_cli_options(kwargs)

    click.echo(kwargs)

    from pip2nix.main import main
    import sys
    main(sys.argv[2:])
