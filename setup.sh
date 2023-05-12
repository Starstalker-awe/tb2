#!/bin/sh
rm genpass.py data.db pass.txt setup.sql 2> /dev/null

if ! which sqlite3 > /dev/null; then
	read -p "sqlite not found! Install? (Y/n) " install
	if [ "$install" != "n" ]; then
		sudo apt-get install sqlite3
	fi
fi

if ! which python3 > /dev/null; then
	read -p "python3 not found! Install? (Y/n) " install
	if [ "$install" != "n" ]; then
		sudo apt-get install python3
	fi
fi

touch data.db
sqlite3 data.db < schema.sql

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt > /dev/null

echo "INSERT INTO setting (name, value) VALUES ('logging_level', 'INFO')" > setup.sql
sqlite3 data.db < setup.sql

echo "from random import randint; print(''.join(list(map(lambda _:(c:='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')[randint(0,len(c)-1)],[None]*16))))" > genpass.py 
password="$(python3 genpass.py)"
echo -n "$password" > pass.txt

# TODO: disable logging
printf "from helpers.settings import HASH_SETTINGS; from passlib.hash import argon2; print(argon2.using(**HASH_SETTINGS).hash('%s'))" "$password" > genpass.py
printf "INSERT INTO user (id, username, password_, p_id, controls) VALUES (1, 'admin', '%s', '%s', 1);" $(python3 genpass.py) "$(uuidgen -r)" > create_user.sql

deactivate

#echo "admin: $password"

sqlite3 data.db < create_user.sql
rm -f create_user.sql genpass.py setup.sql 2> /dev/null

read -p "Enter your IP/domain name(s) (CSV), leave blank for no SSL (not recommended): " domains
if [[ ! -z "$domains" || $1 ]]; then
	read -p "Enter an email you regularly check: " email

	sudo python3 -m venv /opt/certbot
	sudo /opt/certbot/bin/pip install --upgrade pip
	sudo /opt/certbot/bin/pip install certbot certbot
	sudo certbot -n -d "$domains" -m "$email" --redirect --agree-tos

	crontab -l > ccron
	printf "CRON_TZ=America/New_York\n00 00 1 * * /home/user/%s/tb2/helpers/ssl.sh" $(id -u -n) > ccron
	crontab ccron
	rm -f ccron
fi

# Configure Nginx with domain name(s)

export DEBUG=False

unset -v password && unset -v install && unset -v domains && unset -v install