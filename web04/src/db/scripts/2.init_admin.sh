#!/bin/sh

# Load admin password from environment variable
ADMIN_PASSWORD=${ADMIN_PASSWORD:-default_password}

# MySQL Command
echo "
INSERT INTO USERS (id, username, password, css)
VALUES ('2a31e84a-11f6-11f0-ae92-56571f0b6a62', 'admin', '${ADMIN_AUTH_TOKEN}', '1.04')
ON DUPLICATE KEY UPDATE password=VALUES(password);
" | mysql -u root -p"$MYSQL_ROOT_PASSWORD" -D chall && echo "Admin user initialized."

