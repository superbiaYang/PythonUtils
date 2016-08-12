import httplib
import urllib 
import hashlib
import urlparse
import json
import os
import time
import datetime
import logging

import conf

public_key = conf.public_key
private_key = conf.private_key
region = conf.region
project_id = conf.project_id
save_path = conf.save_path
db_id = conf.db_id

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='runtimelog.log',
                filemode='a')

def _verfy_ac(private_key, params):
    items=params.items()
    
    items.sort()

    params_data = "";
    for key, value in items:
        params_data = params_data + str(key) + str(value)
    params_data = params_data + private_key

    sign = hashlib.sha1()
    sign.update(params_data)
    signature = sign.hexdigest()

    return signature

def _set_public_param(params):
    params['PublicKey'] = public_key
    params['ProjectId'] = project_id
    params['Signature'] = _verfy_ac(private_key, params)
    return

def _send_http_request(params):
    httpClient = None

    try:
        data = urllib.urlencode(params) 
        httpClient = httplib.HTTPConnection('api.ucloud.cn', httplib.HTTP_PORT)
        httpClient.request('GET', '/?' + data)

        response = httpClient.getresponse()
        if response.status != httplib.OK:
            raise ValueError('Request backup list failed http status ' + response.status)

        ret = json.loads(response.read())
        if ret['RetCode'] != 0:
            raise ValueError('Request backup list failed ret code ' + str(ret['RetCode']) + ', ' + ret['Message'])

        return ret
    except Exception, e:
        logging.error(e)
        return
    finally:
        if httpClient:
            httpClient.close()

def _get_backup_id():
    params = {}
    params['Action'] = 'DescribeUDBBackup'
    params['Region'] = region
    params['Offset'] = 0
    params['Limit'] = 20
    _set_public_param(params)
    ret = _send_http_request(params)
    if ret:
        return ret['DataSet'][0]['BackupId']
    else:
        return

def _get_backup_url(DBId, BackupId):
    params = {}
    params['Action'] = 'DescribeUDBInstanceBackupURL'
    params['Region'] = region
    params['DBId'] = DBId
    params['BackupId'] = BackupId
    _set_public_param(params)
    ret = _send_http_request(params)
    if ret:
        return ret['BackupPath']
    else:
        return

def _download(url):
    filename = time.strftime('%Y-%m-%d %H-%M-%S') + ".tar.gz"
    path = os.path.join(save_path,filename)
    urllib.urlretrieve(url,path)
    logging.info('Backup success: ' + path)
    return

def _get_backup():
    logging.info('Start backup')
    backup_id = _get_backup_id()
    if backup_id:
        url = _get_backup_url(db_id,backup_id)
        if url:
            _download(url)
    return

def _main():
    while 1:
        _get_backup();
        now = datetime.datetime.now()
        now = now - datetime.timedelta(hours=now.hour,
                                       minutes=now.minute,
                                       seconds=now.second,
                                       microseconds=now.microsecond)
        now = now + datetime.timedelta(hours = 3)
        if now < datetime.datetime.now():
            now = now + datetime.timedelta(days = 1)

        time.sleep((now - datetime.datetime.now()).seconds)
    return

_main()