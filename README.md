# Dead Project - xygt has rebranded to pasted.sh - undergoing rewrite, project archived for now.

![xygt.png](xygt.png)

This repository hosts all of the code for the file hosting site 'xygt.cc'.

![Static Badge](https://img.shields.io/badge/xygt.cc-view%20site-black?link=https%3A%2F%2Fxygt.cc)

## About
xygt.cc is a simple, anonymous, temporary file-hosting service, designed with Python and Flask.

This uses MongoDB by default for the file index, user database, and the URL shortening DB, I'm **not** adding support for SQL.

## Website
You can access the site on [https://xygt.cc](https://xygt.cc).

## License
This project is licensed under the MIT License, which can be found [here](LICENSE) on the git repo.
If you did not recieve a copy of the MIT License with this software, you can view a copy [https://opensource.org/license/mit/](here).

## Contributing
Refer to [CONTRIBUTING](CONTRIBUTING)

## Forking
I don't mind if xygt is forked by anyone into a different project, all I ask is for some credit somewhere in the repo with a link back to here.

Thats it.

## How to run?
1. Clone the repository with `git clone https://github.com/jackeilles/xygt.git`
2. Create a virtual environment in the repository folder `python -m venv .venv`
3. Enter that venv with `source .venv/bin/activate` on Linux/MacOS or `.venv/scripts/activate` on Windows
4. Install "requirements.txt" with `pip install -r requirements.txt`
5. Run with whatever WSGI compatible runner you use, for example `flask run`
