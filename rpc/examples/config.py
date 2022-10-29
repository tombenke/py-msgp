"""Common configuration parameters"""

URL = "nats://127.0.0.1:4222"
RPC_CLIENT_ID = "test-client"
RPC_SERVER_ID = "test-server"
TEST_TOPIC = "test-rpc-topic-name"
TEST_PAYLOAD = b"test payload..."
TEST_HEADERS = {
    "message-type": "TestMessageType",
    "content-type": "text/plain",
    "content-encoding": "utf8",
}
