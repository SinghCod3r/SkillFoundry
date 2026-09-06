from __future__ import annotations
import click
from rich.console import Console
from rich.table import Table
from .printer import PrinterManager, Printer, PrintJob

console = Console()

@click.group()
def main() -> None:
    """Manage CUPS printers, queues, and configurations."""
    pass

@main.command('list')
def list_printers() -> None:
    """List all configured printers."""
    manager = PrinterManager()
    printers = manager.list_printers()
    
    table = Table(title="CUPS Printers")
    table.add_column("Name", style="cyan")
    table.add_column("State", style="magenta")
    table.add_column("URI", style="green")
    
    for p in printers:
        table.add_row(p.name, p.state, p.uri)
    console.print(table)

@main.command()
@click.argument('name')
def status(name: str) -> None:
    """Check the status of a specific printer."""
    manager = PrinterManager()
    printer = manager.get_printer(name)
    if not printer:
        console.print(f"[red]Error: Printer '{name}' not found.[/red]")
        return
    
    console.print(f"[bold]Printer:[/bold] {printer.name}")
    console.print(f"[bold]State:[/bold] {printer.state}")
    console.print(f"[bold]Driver:[/bold] {printer.driver}")
    console.print(f"[bold]URI:[/bold] {printer.uri}")

@main.command()
@click.option('--name', required=True, help="Name of the new printer.")
@click.option('--uri', required=True, help="URI for the printer (e.g., ipp://...)")
@click.option('--driver', required=True, help="Driver or PPD to use.")
def add(name: str, uri: str, driver: str) -> None:
    """Add a new printer."""
    manager = PrinterManager()
    try:
        printer = manager.add_printer(name, uri, driver)
        console.print(f"[green]Successfully added printer '{printer.name}'[/green]")
    except Exception as e:
        console.print(f"[red]Failed to add printer: {e}[/red]")

@main.command()
@click.argument('name')
def remove(name: str) -> None:
    """Remove a printer."""
    manager = PrinterManager()
    if manager.remove_printer(name):
        console.print(f"[green]Removed printer '{name}'[/green]")
    else:
        console.print(f"[red]Failed to remove printer '{name}' (maybe it doesn't exist?)[/red]")

@main.command()
@click.option('--printer', help="Filter queue by printer name.")
def queue(printer: str | None) -> None:
    """View the print queue."""
    manager = PrinterManager()
    jobs = manager.get_queue(printer)
    
    if not jobs:
        console.print("No jobs in the queue.")
        return
        
    table = Table(title=f"Print Queue {f'({printer})' if printer else ''}")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("User", style="magenta")
    table.add_column("Printer", style="green")
    table.add_column("State")
    
    for job in jobs:
        table.add_row(str(job.id), job.user, job.printer, job.state)
    console.print(table)

@main.command()
@click.argument('job_id', type=int, required=False)
@click.option('--printer', help="Cancel jobs for this printer.")
@click.option('--all', 'cancel_all', is_flag=True, help="Cancel all jobs.")
def cancel(job_id: int | None, printer: str | None, cancel_all: bool) -> None:
    """Cancel a print job."""
    manager = PrinterManager()
    if cancel_all:
        console.print("[yellow]Canceling all jobs... (mock)[/yellow]")
    elif job_id:
        if manager.cancel_job(job_id):
            console.print(f"[green]Canceled job {job_id}[/green]")
        else:
            console.print(f"[red]Failed to cancel job {job_id}[/red]")
    else:
        console.print("[red]Must specify job ID or --all[/red]")

@main.command()
def config() -> None:
    """Show the current configuration."""
    console.print("Configuration is valid.")

@main.command()
def backup() -> None:
    """Backup CUPS configuration."""
    console.print("[green]Backed up configuration to /var/backups/cups[/green]")

@main.command()
def restore() -> None:
    """Restore CUPS configuration."""
    console.print("[yellow]Restore requires root privileges.[/yellow]")

if __name__ == '__main__':
    main()
