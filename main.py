from pymocker.mgmt.mgmt_api import run_mgmt_server
# from pymocker.proxy.proxy_server import proxy_server
from pymocker.app_init import db


db.create_all()

run_mgmt_server()
