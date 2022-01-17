py-msgp
=======

[![Quality Check Status](https://github.com/tombenke/py-msgp/workflows/Quality%20Check/badge.svg)](https://github.com/tombenke/py-msgp)
[![Release Status](https://github.com/tombenke/py-msgp/workflows/Release/badge.svg)](https://github.com/tombenke/py-msgp)
![Coverage](./coverage.svg)

Python implementation of generic messaging patterns.

A general purpose messaging library that provides a neutral API for the most used communication patterns, like pub-sub, request-response, etc.

The main purpose of the `messenger` package is to provide an abstraction layer on top of the messaging middlewares.

It defines a generic interface to open the connection to the queues and topics of the middleware and to access to these data-stream using the typical messaging patterns, see the [Messaging Patterns Overview](https://www.enterpriseintegrationpatterns.com/patterns/messaging/index.html) of the Enterprise Integration Patterns for further details.

The implementation relies on the following technologies:
- [NATS](https://nats.io/),
- [NATS streaming](https://nats.io/download/nats-io/nats-streaming-server/).
- [NATS - Python3 Client for Asyncio](https://github.com/nats-io/nats.py) An asyncio Python client for the NATS messaging system.
- [NATS Streaming Python3/Asyncio Client](https://github.com/nats-io/stan.py) An asyncio based Python3 client for the NATS Streaming messaging system platform.
- [nats.py v2.0.0 - docs](https://nats-io.github.io/nats.py/releases/v2.0.0.html)

