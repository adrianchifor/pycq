# pycq
Simple distributed FIFO queue for Python using CockroachDB/PostgreSQL.

Exactly-once processing of messages. Holds all queues in a single table. Supports [psycopg2](https://pypi.org/project/psycopg2/) driver.

Benchmarks for [CockroachDB 3-node cluster](https://www.cockroachlabs.com/docs/stable/orchestrate-cockroachdb-with-kubernetes.html) on Kubernetes:
- n1-standard-1 nodes with standard disk ~ 300 ops/sec
- n1-highcpu-2 nodes with ssd disk ~ 700 ops/sec
- n1-highcpu-16 nodes with ssd disk ~ 4500 ops/sec

## Install
```
pip3 install --user pycq
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

queue = CQ(conn, table="queue") # Default table used is 'queue'
queue.put("example", {"foo": "bar"})

conn.close()
```

### Consumer
```python
import time
import psycopg2
from pycq import CQ

conn = psycopg2.connect(database=<database>,
                        user=<consumer>,
                        host=<host>,
                        port=26257)

queue = CQ(conn)

def process(message):
  # Do stuff with message["data"]

while True:
  message = queue.get("example")
  if message:
      print(f"{message}")
      # {
      #   'data': {'foo': 'bar'},
      #   'enqueued_at': datetime.datetime(2018, 11, 24, 20, 00, 0, 251690)
      # }
      process(message)

  time.sleep(0.1) # Be nice to the system

conn.close()
```
