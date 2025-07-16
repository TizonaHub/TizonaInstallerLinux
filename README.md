# TizonaHub Installer for Linux

## Overview

TizonaHubInstallerLINUX is a simple, automated installer script for setting up **TizonaServer** and **TizonaClient** on Linux systems. It is designed to streamline the deployment process by detecting your environment, installing necessary dependencies, and configuring services.

## Supported Distributions

- **Ubuntu Desktop**
- **Ubuntu Server**
- **Linux Mint**

These distributions share a common base (Debian), so this installer should work reliably on them. It may also work on other Debian-based distributions, but **compatibility is not guaranteed** beyond the officially supported ones.

## Prerequisites

- A user with **sudo** privileges
- Internet access to download packages and repositories
- Optional: Node.js and MySQL/MariaDB. If not installed, the installer can offer to install them for you.

## Troubleshooting

- **Unsupported distribution**: If the installer aborts due to an unsupported OS, consider adapting the script, running on a supported distro or installing manually TizonaHub.
- **Permission errors**: Ensure your user has `sudo` privileges and that the script is executable.
- **Network issues**: Verify internet connectivity and DNS settings.

## License

This installer is distributed under the MIT License. See [LICENSE](LICENSE) for details.
