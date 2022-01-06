py-messenger
============

A general purpose messaging library that provides a neutral API for the most used communication patterns, like pub-sub, JSON-RPC, etc.

The main purpose of the `messenger` package is to provide an abstraction layer on top of the messaging middlewares.

It defines a generic interface to open the connection to the queues and topics of the middleware and to access to these data-stream using the typical messaging patterns, see the [Messaging Patterns Overview](https://www.enterpriseintegrationpatterns.com/patterns/messaging/index.html) of the Enterprise Integration Patterns for further details.

The implementation relies on the following technologies:
- [NATS](https://nats.io/),
- [NATS streaming](https://nats.io/download/nats-io/nats-streaming-server/).

