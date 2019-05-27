# pycq
Simple distributed FIFO queue for Python using CockroachDB/PostgreSQL.

Exactly-once processing of messages. Holds all queues in a single table. Supports [psycopg2](https://pypi.org/project/psycopg2/) driver.

Benchmarks for [CockroachDB 3-node cluster](https://www.cockroachlabs.com/docs/stable/orchestrate-cockroachdb-with-kubernetes.html) on Kubernetes:
- n1-standard-1 nodes with standard disk ~ 300 ops/s
- n1-highcpu-2 nodes with ssd disk ~ 700 ops/s
- n1-highcpu-16 nodes with ssd disk ~ 4500 ops/s

## Install
```
pip3 install pycq
```

## DB Setup
Create the users to use in publishers/consumers:
```sql
CREATE USER IF NOT EXISTS <publisher>;
CREATE USER IF NOT EXISTS <consumer>;
```
Create the queues table:
```sql
CREATE TABLE IF NOT EXISTS queue (
  id SERIAL PRIMARY KEY,
  queue STRING NOT NULL,
  data JSONB NOT NULL,
  enqueued_at TIMESTAMP DEFAULT NOW()
);
```
Create the indexes:
```sql
CREATE INDEX ON queue (queue, enqueued_at) STORING (data);
```
Grant permissions:
```sql
GRANT INSERT ON TABLE queue TO <publisher>;
GRANT SELECT,DELETE ON TABLE queue TO <consumer>;
```

## Usage
### Publisher
```python
import psycopg2
from pycq import CQ

conn = psycopg2.connect(database=<database>,
                        user=<publisher>,
                        host=<host>,
                        port=26257)

queue = CQ(conn, table="queue")  # Default table is 'queue'
queue.put("example", {"foo": "bar"})

conn.close()
```

### Consumer
```python
import psycopg2
from pycq import CQ

conn = psycopg2.connect(database=<database>,
                        user=<consumer>,
                        host=<host>,
                        port=26257)

queue = CQ(conn)

def handler(message):
    print(f"{message}")
    # {
    #   'data': {'foo': 'bar'},
    #   'enqueued_at': datetime.datetime(2019, 5, 12, 17, 46, 57, 351679)
    # }

try:
    queue.subscribe("example", callback=handler,
        # The following are optional and default values
        # e.g. Poll every 0.5s after a message is found or polling has just started.
        #      Switch to polling every 2s if the queue stays empty for 10s.
        poll_interval=2.0,
        burst_poll_interval=0.5,
        burst_decay_interval=10.0
    )
except KeyboardInterrupt:
    conn.close()
```
