from __future__ import annotations
import pytest
from cups_admin.printer import PrinterManager, Printer, PrintJob

def test_list_printers():
    manager = PrinterManager()
    printers = manager.list_printers()
    assert len(printers) == 2
    assert any(p.name == "HP-LaserJet" for p in printers)

def test_get_printer():
    manager = PrinterManager()
    printer = manager.get_printer("HP-LaserJet")
    assert printer is not None
    assert printer.name == "HP-LaserJet"
    
    missing = manager.get_printer("Non-Existent")
    assert missing is None

def test_add_printer():
    manager = PrinterManager()
    printer = manager.add_printer("New-Printer", "ipp://test", "generic")
    assert printer.name == "New-Printer"
    assert len(manager.list_printers()) == 3

def test_remove_printer():
    manager = PrinterManager()
    assert manager.remove_printer("HP-LaserJet") is True
    assert len(manager.list_printers()) == 1
    assert manager.remove_printer("HP-LaserJet") is False

def test_get_queue():
    manager = PrinterManager()
    queue = manager.get_queue()
    assert len(queue) == 2
    
    filtered = manager.get_queue("HP-LaserJet")
    assert len(filtered) == 1
    assert filtered[0].printer == "HP-LaserJet"

def test_cancel_job():
    manager = PrinterManager()
    assert manager.cancel_job(1) is True
    assert manager.cancel_job(999) is False
