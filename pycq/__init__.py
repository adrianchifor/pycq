import json
from psycopg2.extensions import TransactionRollbackError


class CQError(Exception):
    """
    Generic CQ error
    """
    pass


class CQ(object):
    def __init__(self, conn, table: str = "queue"):
        """
        Construct new CQ object
        :param conn: psycopg2 connection
        :param table: name of table to use for queue (default 'queue')
        :return: returns CQ object instance
        """
        if not conn:
            raise CQError("CQ(conn): conn cannot be None")
        if not table:
            raise CQError("CQ(conn, <table>): table cannot be None and must have length greater than 0")

        self.conn = conn
        self.table = table

    def put(self, queue: str, data: dict) -> bool:
        """
        Put message in queue
        :param queue: name of queue
        :param data: dictionary to attach to the message in the queue
        :return: true if successfully added, false otherwise
        """
        if not queue:
            raise CQError("put(<queue>, data): queue cannot be None and must have length greater than 0")
        if not data:
            raise CQError("put(queue, <data>): data cannot be None and must have at least one key")

        data_json = json.dumps(data)
        with self.conn:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO {} (queue, data)
                    VALUES (%s, %s);
                    """.format(self.table),
                    (queue, data_json))
                return True

        return False

    def get(self, queue: str) -> dict:
        """
        Get first message in queue
        :param queue: name of queue
        :return: message as dictionary, None if queue is empty
        """
        if not queue:
            raise CQError("get(queue): queue cannot be None and must have length greater than 0")

        try:
            with self.conn:
                with self.conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, data, enqueued_at FROM {}
                        WHERE queue = %s
                        ORDER BY enqueued_at ASC
                        LIMIT 1;
                        """.format(self.table),
                        (queue,))
                    message = cursor.fetchone()
                    if message:
                        cursor.execute("""
                            DELETE FROM {} WHERE id = %s;
                            """.format(self.table),
                            (message[0],))

                        return {"data": message[1], "enqueued_at": message[2]}
        except TransactionRollbackError:
            # Message already picked up by another worker
            pass

        return None
