#!/usr/bin/env python3
# Run the app - MADE FOR SYSTEMD SERVICE

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)

########################################