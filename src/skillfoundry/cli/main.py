from __future__ import annotations

import sys
import traceback

import click

from skillfoundry import __version__

# Subcommands will be imported and registered here
from skillfoundry.cli.build import build
from skillfoundry.cli.compare import compare
from skillfoundry.cli.eval_cmd import eval_cmd
from skillfoundry.cli.improve import improve
from skillfoundry.cli.output import Output
from skillfoundry.cli.validate import validate
from skillfoundry.config import load_config


class ContextObject:
    """Context object to pass state to commands."""
    def __init__(self, output: Output, verbose: bool):
        self.output = output
        self.verbose = verbose
        try:
            self.settings = load_config()
        except Exception:
            self.settings = None

class SafeGroup(click.Group):
    """A Click group that gracefully handles exceptions."""
    def invoke(self, ctx: click.Context) -> None:
        try:
            return super().invoke(ctx)
        except click.exceptions.Exit:
            raise
        except click.exceptions.Abort:
            raise
        except click.exceptions.ClickException:
            raise
        except Exception as e:
            obj = ctx.obj
            if obj and obj.verbose:
                traceback.print_exc()
            if obj:
                obj.output.error(str(e))
            else:
                click.echo(f"✗ {e!s}", err=True)
            sys.exit(1)

@click.group(cls=SafeGroup)
@click.version_option(version=__version__, prog_name='skillfoundry')
@click.option('--verbose', is_flag=True, help='Enable verbose output.')
@click.option('--quiet', is_flag=True, help='Suppress non-essential output.')
@click.option('--json', 'json_output', is_flag=True, help='Output results as JSON.')
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool, json_output: bool) -> None:
    """SkillFoundry CLI."""
    output = Output(quiet=quiet, json_mode=json_output)
    ctx.obj = ContextObject(output=output, verbose=verbose)

cli.add_command(build)
cli.add_command(validate)
cli.add_command(eval_cmd, name='eval')
cli.add_command(improve)
cli.add_command(compare)
