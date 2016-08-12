# Some Answers
## Which share of web users will this implementation address? Should it be increased and how?
This implementation requires a recent browser that supports HTML 5 and
Websockets. This is very common nowadays so I'd say this implementation
addresses a very large share of web users. We could even have a broader support
by developing a native application but this is platform dependent so it's
more expensive to develop.

## How many users can connect to one server?
I used the script in tools/stresser.py to open a big number of concurrent
web socket sessions. I can easily reached 30k simultaneous connections on
my small laptop. I am pretty sure that thus implementation can do 100k+
connections on a real server thanks to the usage of asynchronous IO.


## How can the system support more systems?
I'd distribute the service on several servers, using Redis as the common
datastore. Then I'll try to find a software load balancer that can handle
1M concurrent connections and if that doesn't exist do DNS load-balancing
although that comes with its caveats.

## How to reduce the attack surface of the systems?
The application is rather simple with a single entry point. The biggest concern
is DoS attacks: I'd implement a Web socket connections rate limit and Websocket
messages rate limit.

## Should an authentication mechanism be put in place and if yes, how?
Of course. This implementation is terrible, the client (i.e the browser)
declares its identity ("Hey I am client A") but we should never trust the client.
So authentication is required. I'd start with something simple like HTTP digest
access authentication (over HTTPS) because it's standard and supported by
browsers and web servers so it should play nice with websockets. If it's not
considered secure enough, I'd try to use another existing authentication
mechanism maybe based on HMAC. But I wouldn't try to come with a new /ivented
solution, crypto is too hard for me.

