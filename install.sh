# Might dockerise this stuff sooner or later, not now tho.

if [ $EUID -ne 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

apt install mongodb-org python3-pip python3-venv

systemctl enable --now mongod

cp autoclean-xygt.service /lib/systemd/system/
cp autoclean.py /usr/bin/
cp config.py /usr/bin/

systemctl enable --now autoclean-xygt.service

echo "Installation complete, launch xygt with ./run.py (in the venv)"