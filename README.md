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
- [NATS JetStream](https://github.com/nats-io/jetstream),
- [Python3 client for the NATS messaging system](https://nats-io.github.io/nats.py/).

__IMPORTANT NOTE:__
This version of the package uses the NATS JetStream for durable functions.
In case you need the [NATS streaming](https://nats.io/download/nats-io/nats-streaming-server/)
use the older version of this package before v1.0.0.

## License
The scripts and documentation in this project are released under the [MIT License](LICENSE)

