#!/bin/sh

# Setup a context to the development server
nats context add dev --server nats:4222 --description "Development server" --select

