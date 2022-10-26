"""Common configuration parameters for test cases"""

URL = "nats://127.0.0.1:4222"
CLIENT_ID = "test-client"
TEST_TOPIC = "test-topic-name"
TEST_TOPIC_DURABLE = "test-topic-durable-name"
TEST_PAYLOAD = b"test payload..."
TEST_HEADERS = {"message-type": "PlainTextMsgType", "representation": "plain/text"}
