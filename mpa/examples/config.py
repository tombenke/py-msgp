"""Common configuration parameters for examples"""

URL = "nats://127.0.0.1:4222"
CONSUMER_MPA_CLIENT_ID = "test-consumer-mpa-client"
PRODUCER_MPA_CLIENT_ID = "test-producer-mpa-client"
PROCESSOR_MPA_CLIENT_ID = "test-processor-mpa-client"
PROCESSOR_INBOUND_TOPIC = "mpa-processor-inbound-topic"
PROCESSOR_OUTBOUND_TOPIC = "mpa-processor-outbound-topic"
TEST_PAYLOAD = b"test payload..."
TEST_HEADERS = {
    "message-type": "TestMessageType",
    "content-type": "text/plain",
    "content-encoding": "utf8",
}
