# pygdo-hydra-server

Token-based monitoring server for PyGDO and PHPGDO clients.

## First vertical slice

`$hydra_server.acquire [name]` creates a monitor without requiring a GDO account.
It generates a random 16-character ASCII token as the primary key and a
separate random password. The database stores only the bcrypt password hash.

Client registration and health checks intentionally follow in separate steps.

`GDO_HydraHistory` is the append-only resource history: CPU load, RAM, disk
and project storage are all recorded in bytes where applicable.
Token-based Hydra monitoring server for PyGDO clients.
