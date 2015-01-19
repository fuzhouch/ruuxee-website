#Server-end Design Doc

The server-end code is represented as a set of WSGI-compatible
applications, written in Python.

##Frameworks and dependencies

The application uses flask framework.

##Folder structure

    server/
        ruuxee/     => ruuxee module.
            config/ => Configuration scripts to initialize app.
                webui_dev.py => Configuration for UI developers.

            models/ => Database representation.
            views/  => UI views that binds to web pages.
                signin.py   => Sign-in/sign-up page view.
                timeline.py => User timeline view.
                person.py   => User information page.

            apis/   => HTTP-based RESTful API handlers.
                ... v1 => Version 1 Ajax APIs.

            utils/  => Helper functions.
            templates/ => [TO BD ADDED] Template HTML, used with views.
            static/ [TO BE ADDED] => Static functions

NOTES:

1. All Views must be inherited from ruuxee.View, to keep unified
   template structure.

2. Both APIs and views are implemented as flask blueprints. The only
   difference is, APIs does not handle UIs, while views have their
   corresponding web page templates.
