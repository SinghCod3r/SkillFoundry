# cups-admin API Reference

## PrinterManager

The `PrinterManager` class handles operations against the CUPS server.

### Methods

#### `list_printers() -> List[Printer]`
Returns a list of all configured printers.

#### `get_printer(name: str) -> Optional[Printer]`
Fetches a specific printer by its name. Returns `None` if not found.

#### `add_printer(name: str, uri: str, driver: str) -> Printer`
Adds a new printer to the system. Raises `ValueError` if the printer already exists.

#### `remove_printer(name: str) -> bool`
Removes an existing printer. Returns `True` if successful, `False` if the printer did not exist.

#### `get_queue(printer_name: Optional[str] = None) -> List[PrintJob]`
Gets the current print queue. If `printer_name` is specified, filters the queue to only show jobs for that printer.

#### `cancel_job(job_id: int) -> bool`
Cancels a print job by its ID. Returns `True` if the job was found and canceled, `False` otherwise.
