#!/bin/sh
# Remove files that were previously created
rm genpass.py data.db pass.txt setup.sql 2> /dev/null
# Ensure certbot is installed
sudo apt install python3-certbot-nginx -y

# Install sqlite3 if not installed
if ! which sqlite3 > /dev/null; then
	read -p "sqlite not found! Install? (Y/n) " install
	if [ "$install" != "n" ]; then
		sudo apt-get install sqlite3 -y
	fi
fi

# Install python3 if not installed
if ! which python3 > /dev/null; then
	read -p "python3 not found! Install? (Y/n) " install
	if [ "$install" != "n" ]; then
		sudo apt-get install python3 -y
	fi
fi

# Touch database and run schema file on it
touch data.db && sqlite3 data.db < schema.sql

# Configure all usage of python; pip installations, password generation, admin user creation in DB
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Insert default settings into database
echo "INSERT INTO setting (name, value) VALUES ('logging_level', 'INFO')" > setup.sql
sqlite3 data.db < setup.sql

# Generate random admin password
echo "from random import randint; print(''.join(list(map(lambda _:(c:='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-=_+,./<>?')[randint(0,len(c)-1)],[None]*16))))" > genpass.py 
password="$(python3 genpass.py)"
echo -n "$password" > pass.txt

# Hash password and insert into database
printf "from helpers.settings import HASH_SETTINGS; from passlib.hash import argon2; print(argon2.using(**HASH_SETTINGS).hash('%s'))" "$password" > genpass.py
printf "INSERT INTO user (id, username, password_, p_id, controls) VALUES (1, 'admin', '%s', '%s', 1);" $(python3 genpass.py) "$(uuidgen -r)" > create_user.sql

deactivate

#echo "admin: $password"

sqlite3 data.db < create_user.sql
rm -f create_user.sql genpass.py setup.sql 2> /dev/null

# Configure SSL certificate
if [ ! $1 ]; then
	read -p "Enter your IP/domain name: " domain
else
	domain=$1
fi

if [ ! $2 ] ; then
	read -p "Do you want an SSL certificate? (recommended) (Y/n): " ssl
	if [[ -z "$ssl" || $2 ]]; then
		if [ ! $3 ]; then
			read -p "Enter an email you regularly check: " email
		else
			email=$3
		fi

		sudo python3 -m venv /opt/certbot
		sudo /opt/certbot/bin/pip install --upgrade pip
		sudo /opt/certbot/bin/pip install certbot certbot
		sudo certbot certonly -n --nginx -d "$domain" -m "$email" --redirect --agree-tos

		crontab -l > ccron
		printf "CRON_TZ=America/New_York\n00 00 1 * * /home/$(id -u -n)/tb2/setup/ssl.sh" > ccron
		crontab ccron
		rm -f ccron
	fi
fi

# Configure Nginx with domain name(s)
bash ./template/service.sh > /etc/systemd/system/tb2.service
sudo systemcl start tb2 && sudo systemcl enable tb2 && sudo systemcl status tb2

bash ./templates/nginx.sh $domain > /etc/nginx/sites-available/tb2
sudo ln -s /etc/nginx/sites-available/tb2 /etc/nginx/sites-enabled
if sudo nginx -t; then
	echo -e "\nNginx test passed!\n"
else
	echo -e "\nNginx test failed! Exiting!\n" && exit(1)
fi

export DEBUG=False
unset -v password && unset -v install && unset -v domain && unset -v install && unset -v ssl
rm -rf 

echo -e "\n\nEverything has been installed and configured properly,\nyour web server should be running at https://'$domain'\n\n"