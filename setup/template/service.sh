#!/bin/sh
USER="$(id -u -n)"
cat << EOF
[Unit]
Description=Gunicorn instance to run tb2.wsgi
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/home/$USER/tb2
Environment="PATH=/home/$USER/tb2/venv/bin"
ExecStart=/home/$USER/tb2/venv/bin/gunicorn -w 1 --bind unix:tb2.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOF