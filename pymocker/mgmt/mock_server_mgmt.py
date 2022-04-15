from pymocker.mgmt.mock_server_model import MockServerInstance, MockServerRecord
from pymocker.engine.drivers import EngineDriver
import requests
import json
import time
from pymocker.app_init import db
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class MockServerMgmt:
    mock_server_instances = {}

    @classmethod
    def add_mock_server(cls, req_data):
        reverse_target_url = req_data.get('target_url')
        mock_rules = req_data.get('mock_rules', [])
        mock_server_id = req_data.get('mock_server_id')

        if mock_server_id in cls.mock_server_instances:
            return False, f"mock_server_id {mock_server_id} has existed"
        record = MockServerRecord.query.filter_by(mock_server_id=mock_server_id).first()
        if record:
            return False, f"mock_server_id {mock_server_id} has existed"

        if not mock_server_id:
            mock_server_id = str(time.time())

        try:
            if isinstance(mock_rules, bytes):
                mock_rules = mock_rules.decode()
            if isinstance(mock_rules, str):
                mock_rules = json.loads(mock_rules)
        except Exception as e:
            return False, f'Error: format of mock_rules is not list, {str(e)}'

        record = MockServerRecord(
            mock_server_id=mock_server_id,
            target_url=reverse_target_url,
            mock_rules=mock_rules
        )
        db.session.add(record)
        db.session.commit()
        print('Mock server created', record)
        mock_server = MockServerInstance(record)
        cls.mock_server_instances[mock_server.mock_server_id] = mock_server
        # cls.start_mock_server(mock_server_id)

    @classmethod
    def list_mock_servers(cls):
        results = []
        records = MockServerRecord.query.all()
        for r in records:
            if r.mock_server_id in cls.mock_server_instances:
                t = cls.mock_server_instances[r.mock_server_id]
            else:
                t = MockServerInstance(r)
                cls.mock_server_instances[t.mock_server_id] = t
            results.append(t)
        return results

    @classmethod
    def get_mock_server(cls, mock_server_id):
        if mock_server_id in cls.mock_server_instances:
            return cls.mock_server_instances.get(mock_server_id)
        else:
            record = MockServerRecord.query.filter_by(mock_server_id=mock_server_id).first()
            if record:
                t = MockServerInstance(record)
                cls.mock_server_instances[t.mock_server_id] = t
                return t
            else:
                return None

    @classmethod
    def put_mock_server(cls, mock_server_id, req_data):
        if isinstance(req_data, dict):
            rules = req_data.get('mock_rules', [])
        else:
            rules = req_data
        try:
            if isinstance(rules, bytes):
                rules = rules.decode()
            if isinstance(rules, str):
                rules = json.loads(rules)
        except Exception as e:
            return False, f'Error: format of mock_rules is not list, {str(e)}'

        # update db
        record = MockServerRecord.query.filter_by(mock_server_id=mock_server_id).first()
        if not record:
            return False, "Not Found"
        record.mock_rules = rules
        db.session.commit()

        # update mock server instance if has
        mock_server: MockServerInstance = cls.mock_server_instances.get(mock_server_id)
        mock_server.mock_rules = rules
        if not mock_server:
            return True, "updated"
        if mock_server.is_running():
            resp = requests.put(url=f"{mock_server.get_access_url()}/mock_rules", json=rules, verify=False)
            if not resp or resp.status_code != 200:
                return False, "Update remote mock server rules failed"
        return True, rules

    @classmethod
    def start_mock_server(cls, mock_server_id):
        mock_server = cls.mock_server_instances.get(mock_server_id)
        if not mock_server:
            record = MockServerRecord.query.filter_by(mock_server_id=mock_server_id).first()
            if not record:
                return False, f"No mock_server_id {mock_server_id} in db"
            mock_server = MockServerInstance(record)
            cls.mock_server_instances[mock_server_id] = mock_server
        ins = EngineDriver.get_engine().run(mock_server)
        if ins.is_alive():
            mock_server.set_running()
            print(f'Mock server {mock_server_id} started')
            return True, mock_server.to_dict()
        else:
            print(f'Mock server {mock_server_id} failed to start')
            return False, 'Mock server can not start'

    @classmethod
    def stop_mock_server(cls, mock_server_id):
        p = cls.mock_server_instances.get(mock_server_id)
        if p and p.is_running():
            EngineDriver.get_engine().stop(mock_server_id)
            print('Mock server stopped', mock_server_id)
            ins = cls.mock_server_instances[mock_server_id]
            ins.set_stopped()
            return p
        else:
            return None

    @classmethod
    def delete_mock_server(cls, mock_server_id):
        p = cls.mock_server_instances.get(mock_server_id)
        if p:
            if p.is_running():
                EngineDriver.get_engine().stop(mock_server_id)
                print('Mock server stopped', mock_server_id)
            p.release()
            del cls.mock_server_instances[mock_server_id]
            return p
        record = MockServerRecord.query.filter_by(mock_server_id=mock_server_id).first()
        if record:
            db.session.delete(record)
            db.session.commit()
        print('Mock server deleted', mock_server_id)

