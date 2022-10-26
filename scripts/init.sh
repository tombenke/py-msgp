#!/bin/sh

# Setup a context to the development server
nats context add dev --server nats:4222 --description "Development server" --select

# Create a stream for all events
nats stream add EVENTS \
    --subjects "events.*" \
    --description="Stream for all incoming events." \
    --ack \
    --max-msgs=-1 \
    --max-bytes=-1 \
    --max-age=1y \
    --storage file \
    --retention limits \
    --max-msg-size=-1 \
    --discard old \
    --dupe-window="0s" \
    --replicas 1 \
    --max-msgs-per-subject=-1 \
    --no-allow-rollup \
    --no-deny-delete \
    --no-deny-purge

# Create an ephemeral consumer for new events
nats consumer add EVENTS MONITOR \
    --target monitor.events \
    --description="An ephemeral, push-based consumer to monitor the events" \
    --ephemeral \
    --ack none \
    --deliver new \
    --replay instant \
    --filter "" \
    --heartbeat=30s \
    --flow-control \
    --deliver-group="" \
    --no-headers-only \
    --backoff=none

