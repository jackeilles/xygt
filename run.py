#!/usr/bin/env python3

from app import app
from waitress import serve

if __name__ == '__main__':
    serve(app, listen='*:5000')
