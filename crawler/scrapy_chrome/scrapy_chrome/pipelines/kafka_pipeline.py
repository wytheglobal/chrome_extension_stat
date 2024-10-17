from kafka import KafkaProducer
import json

class KafkaPipeline:
    def __init__(self, kafka_brokers, kafka_topic):
        self.kafka_brokers = kafka_brokers
        self.kafka_topic = kafka_topic
        self.producer = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            kafka_brokers=crawler.settings.get('KAFKA_BROKERS'),
            kafka_topic=crawler.settings.get('KAFKA_TOPIC')
        )

    def open_spider(self, spider):
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def close_spider(self, spider):
        if self.producer:
            self.producer.close()

    def process_item(self, item, spider):
        self.producer.send(self.kafka_topic, item)
        return item
