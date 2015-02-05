#Ruuxee Server Design Doc

The server-end code is represented as a set of WSGI-compatible
applications, written in Python.

##Design principles

As a web site server must avoid unexpected server process down.
Unforutately, we know it's impossible to make zero bug in our code. To
make sure we minimize the risk of blocking our business, we need to set
up some basic design principles.

* Rule 0: Don't keep data in memory of running process. This is to make
  sure all server can be restarted when anything wrong happens. Put all
  data in database or cache services.

* Rule 2: Content Operations must be written into database immediately.
  Content Operations are the key of our resources that we must do our
  best to avoid data lose.

* Rule 3: Security data can't be kept as plain text in database. It must
  be hashed or encrypted. Password, session encryption key, fall into
  this category.


##Terminologies

* Roles. Identify different servers in architecture. A role may have one
  or more process running in a server machine, or distributed in
  multiple server machines.

* Entities. Identify concepts of product, such as users and posted
  articles.

* Clients. It means applications running in devices that access
  ruuxee.com, which can be browsers or mobile apps.

* Users. Identify individuals that uses ruuxee.com. Every user should
  represent a real person, and a set of records stored in database.

* Posts. Identify the posted articles by users. A post is represented by
  a record stored in database.

* Topics. Identify a topic under discussion. Every post belongs to one
  and only one topic, while a topic can contain one or more posts.

* Entity. Identify an item that needs to be recorded in database for its
  basic information. Users, posts, topics are considered entities.

* Interaction. Interaction means a request that a user perform to
  change its relationship with another entity. This kind of request
  include: follow, unfollow, upvote, downvote, adding comments, etc.
  Another behavior of interaction is it does not require rich return
  data to client.

* Content Operation. Content Operation nmeans a request that does not
  affect other entities, but generate or modify contents. The request
  include: create account, login, logout, create a post, etc. A
  Content Operation usually returns rich data to client.

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


##High level design of server architecture

The picture below shows a brief of how a server system is constructed.
A complete ruuxee server system contains the follow roles:

* Web Handler & Web API handler.
* Message queue.
* Request worker.
* Database & cache.

    +----------------------+     +---------------+
    |      Web handler     |->>>-| Message queue |
    +----------+-----------+     +-------+-------+
               |                         |
               |                         |   +--------------------+
               |                         +>>>+   Request worker   |
               |                             +----------+---------+
               |                                        |
               |                                        v
               |                                        v
               |                                        |
               |                             +----------+---------+
               +------------->>>-------------+   Database/cache   |
               +-------------<<<-------------+                    |
                                             +--------------------+

Following traditional MVC pattern, we can consider Web page and API
handlers as our View, and Message queue handler + Database workder as
our Controller, then Database/cache as Model. However, this design does
not try to strictly map itself to classic MVC pattern, as this is not
our goal.

###Web Handler and Web API handler

This role receives the direct HTTP request from apps or browsers in
clients' devices. It parses HTTP request and understand its purpose,
then call internal APIs to do real work. It also handles invalid URL and
redirect it to login pages or "NOT FOUND" pages.

The second work for this role, is to render web pages. It takes data
from backend and template from frontend engineers, then render it and
return to browser. This case may be different for apps, as they usually
get direct response (in Json format) from web APIs.

The last work that handled by this role, is authentication. It validates
the user session token and decide if it's authenticated. If a user can't
be authenticated, it redirects the request to login page, instead of
accepting it.

This role can be extended to multiple machines. Indeed, the first
release of Ruuxee server design contains both Web Handler and web
API handlers. We may consider adding more handlers for load balancing
purpose in the future, when we have more user coming in.

This role is implemented under Flask framework.

###Message queue and request worker

When Web Handlers get a valid request from clients, there may be two
kinds of requests:

1. Interaction. Interaction means a request that a user perform to
   change its relationship with another entity. This kind of request
   include: follow, unfollow, upvote, downvote, adding comments, etc.
   Another behavior of interaction is it does not require rich return
   data to client.

2. Content Operation. Content Operation nmeans a request that does not
   affect other entities, but generate or modify contents. The request
   include: create account, login, logout, create a post, etc. A
   Content Operation usually returns rich data to client.

Message queue is used to handle interactions. When a new interaction
request come, the Web Handler leaves a record in message queue, then
returns. The data is kept in the queue, until Request worker picks it
up and perform action.

The reason to introduce message queue is to speed up the Web Handler.
A typical interaction scenario usually contains multiple steps, for
example, when a user follows a topic, the system must a) update the
topic's status, and b) publish it to the feed/timeline of user's followers.
Step b) can be time consuming if a user has a lot of followers, but
actually, these steps do not need to be performed immediately. We should
not block Web Handler to wait for the completion of this kind of
actions. By introducing message queue, we allow Web Handler quickly
return when a request is registered.

Another reason for message queue is to support extension of Web
Handlers. I have mentioned we may have to add more Web Handers when user
base grows. In this case, multiple instances may introduce
inconsistency when an interaction requires multiple steps. With the help
of message queue, all requests can be organized in an atomic way.

At last, please note that message queue is NOT to handle operations.
Because operations usually requires data return to customer, we need to
wait for completion of them.

###Database and cache

Database and cache are the last part of the system. They define the
schema for entities and other actions. Database and cache are not active
servers: they don't perform action to other roles. Instead, other roles
manipulate data stored in them.

Database and cache can be accessed by both interaction worker and web
handler. The reason that web handler access it is because web handler
needs the user information in database for authentication purpose.

##Detailed design

This section talks about details of each role in class/module level.

###Web handler

The web handler role is implemented under Flask framework. It contains
the following modules:

* Flask routers. The entry point. These routers handles Http requests,
  parse URL and validate if requests are from authenticated users. If
  yes, it calls corresponding APIs from DataAccess to process them

* DataAccess. This module understand how to handle requests. It
  distinguishes interaction and operations, and decides how to process
  them. For interactions, DataAccess forwards it to message queue
  worker, by adding a record to message queue. For operations, it
  handles them itself.

* SessionManager. The module to handle authentications.

* Queue, Cache and Database. The interface to storage.

The structure of Web Handler role can be demonstrated with the chart
below.

    +-------+     +------------+     +----------+
    | Flask +-----+ DataAccess +--+--+ Queue    |
    +---+---+     +------------+  |  +----------+
        |                         |
        |                         |  +----------+
        |                         +--+ Cache    |
    +----------------+            |  +----------+
    | SessionManager |            |
    +-------+--------+            |  +----------+
            +---------------------+--+ Database |
                                     +----------+

###Request Worker

Request Worker is simple. It's a single instance running in background,
listening to message queue and handle requests one by one when queue is
not empty. If there's no request worker, all requests will be stored in
this queue, until it's picked up and processed.

###Message queue

We make use of Redis to implement Message queue. Thanks to Redis'
`blpop` and `brpop` commands, we can implement a simple queue by
creating a Redis list.

##Security and authentication

TBD: This section will talk about design of user authentication, aka,
implementation of SessionManager.

##Open topics

###Optimiaztion for user authentication

This is still an open topic because I haven't fully figured out a way to
measure the potential performance cost for this. Under discussion.
