# Troubleshooting Guide for cups-admin

## Printer not found
- Verify the printer name is spelled correctly using `cups-admin list`.
- Check if the CUPS daemon is running: `systemctl status cups`.

## Connection refused
- Check your configuration in `~/.cups-admin/config.toml`.
- Ensure the CUPS server allows remote administration if connecting remotely.
- Port 631 must be open on the host.

## Jobs stuck in queue
- Check the printer state: `cups-admin status PRINTER_NAME`.
- If the printer is paused, resume it via the CUPS web interface or CLI.
- Cancel problematic jobs: `cups-admin cancel --printer PRINTER_NAME --all`.

## Permission denied
- Certain operations (like adding printers) require administrative privileges.
- Ensure your user is in the `lpadmin` group: `sudo usermod -aG lpadmin $USER`.

## Driver not available
- When adding a printer, specify a valid driver name or PPD file.
- Look up available drivers with `lpinfo -m` (standard CUPS command).

## SSL certificate errors
- If connecting to a remote CUPS server with self-signed certs, you may need to disable SSL or add the certificate to your trust store.
