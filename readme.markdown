# RuuXee Project
This is the ruuxee main site project, for production use. It contains
source code to setup Ruuxee web site, including:

* bin/  Scripts and tools for deployment and maintanence.
* docs/ Documentation.
* src/  Source code. Including,
  - src/backend/ Source code for backend applications. Defined by roles.
  - src/frontend/ Source code for frontend (HTML/CSS/JavaScript).

## Get Started

### Checkout source code.

All users can checkout code with command line below:

    git clone https://github.com/present-corp/ruuxee.git
    cd ruuxee # Now all code is here.

## Deployment

RuuXee uses [uwsgi](http://uwsgi-docs.readthedocs.org/en/latest/) to
deploy web servers. The main web server used for RuuXee is Nginx.

Created by Fuzhou Chen, Jan. 11, 2015.
