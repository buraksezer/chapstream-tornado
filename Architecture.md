Design Plans and technologies
=============================

### Basic Design

* I am planning to develop a streaming API as backend app. 
* I will implement a web client that consumes JSON and uses WebSocket to 
  communiciate the server. It will also use regular AJAX calls for doing
  regular operations.
* Most of the backend stuff will be separated from the API application.
  So I am going to use a task queue for doing many jobs. For example, when 
  any user posts a message, only one database operation will be done in that
  HTTP request: inserting of the the message to current users time line table.
  All other things will be done by a task. 
* User time lines will be stored in Redis as a list(actually, a linked list).
  So when someone reach the homepage, this is not trigger a disk intensive 
  database operation. Instead of that the request will run a memory. 
  I am planning to store last 1000 posts for each user in the Redis instance.


### Technologies

* ChapStream will use Python as server side programming.
* Tornado will be used for WebSocket and Web server implementation.
* PostgreSQL for SQL database.
* Redis for caching
* and other well-known applications for managing, scaling and high availability.
* I am going to use AngularJS to implement web client.
* I am planning to use Bootstrap3 as frontend framework.

