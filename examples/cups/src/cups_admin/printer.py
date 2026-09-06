from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Printer:
    """Represents a CUPS printer."""
    name: str
    uri: str
    driver: str
    state: str
    accepting_jobs: bool
    shared: bool

@dataclass
class PrintJob:
    """Represents a job in the CUPS print queue."""
    id: int
    printer: str
    user: str
    title: str
    state: str
    size: int
    submitted_at: datetime

class PrinterManager:
    """Manages CUPS printers and print queues."""
    
    def __init__(self) -> None:
        # Mock data for demonstration purposes
        self._printers = {
            "HP-LaserJet": Printer("HP-LaserJet", "ipp://10.0.0.5/ipp/print", "hpcups", "idle", True, True),
            "Epson-Stylus": Printer("Epson-Stylus", "usb://EPSON/Stylus", "gutenprint", "processing", True, False),
        }
        self._jobs = [
            PrintJob(1, "HP-LaserJet", "ayush", "document.pdf", "pending", 10240, datetime.now()),
            PrintJob(2, "Epson-Stylus", "root", "test_page.txt", "processing", 1024, datetime.now()),
        ]

    def list_printers(self) -> List[Printer]:
        """List all configured printers."""
        return list(self._printers.values())

    def get_printer(self, name: str) -> Optional[Printer]:
        """Get a printer by name."""
        return self._printers.get(name)

    def add_printer(self, name: str, uri: str, driver: str) -> Printer:
        """Add a new printer to CUPS."""
        if name in self._printers:
            raise ValueError(f"Printer {name} already exists.")
        printer = Printer(name, uri, driver, "idle", True, True)
        self._printers[name] = printer
        return printer

    def remove_printer(self, name: str) -> bool:
        """Remove a printer from CUPS."""
        if name in self._printers:
            del self._printers[name]
            return True
        return False

    def get_queue(self, printer_name: Optional[str] = None) -> List[PrintJob]:
        """Get the print queue, optionally filtered by printer name."""
        if printer_name:
            return [j for j in self._jobs if j.printer == printer_name]
        return self._jobs

    def cancel_job(self, job_id: int) -> bool:
        """Cancel a print job by ID."""
        for i, job in enumerate(self._jobs):
            if job.id == job_id:
                job.state = "canceled"
                return True
        return False
