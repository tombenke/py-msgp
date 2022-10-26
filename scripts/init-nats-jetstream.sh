#!/bin/sh

# Wait for the the NATS server to start
until nats pub -s nats://nats:4222 test "Hello NATS"; do echo waiting for NATS; sleep 5; done;

# Setup a context to the test server
nats context add test --server nats:4222 --description "test server" --select

# Create a stream for all test messages
nats stream add MPA_TEST \
    --subjects "test-mpa-inbound-topic-name,test-mpa-outbound-topic-name,test-mpa-durable-inbound-topic-name,test-mpa-durable-outbound-topic-name,test-mpa-durable-inbound-proc-topic-name,test-mpa-durable-outbound-proc-topic-name" \
    --description="Stream for all incoming test messages" \
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

