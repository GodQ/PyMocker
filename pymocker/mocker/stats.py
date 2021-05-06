

class HttpRecordStore:
    http_records = list()

    @classmethod
    def insert_records(cls, item):
        cls.http_records.append(item)

    @classmethod
    def get_http_records(cls):
        return cls.http_records

    @classmethod
    def reset_http_records(cls):
        cls.http_records.clear()
