import os, sys, re, json, random, logging as log, threading, urllib3, requests
from time import time, sleep
TIMEOUT = 10


def punchcard(username, password):
    fields = {
        'fieldDJXXyc': '1',
        'fieldZtw': '1',
        'fieldWantw': '1',
        'fieldSQnj': '1718',
        'fieldSQbj': '24',
        'fieldSQxq': '2',
        'fieldSQgyl': '28',
        'fieldSQqsh': '225'
    }

    conditions = {
        'fieldDJXXyc': '(int(time()%86400/3600)+8)%24 in range(6,12)',
        'fieldZtw': '(int(time()%86400/3600)+8)%24 in range(6,12)',
        'fieldWantw': '(int(time()%86400/3600)+8)%24 in range(21,24)',
    }
    try:
        s = requests.Session()
        s.headers.update({'Referer': 'https://ehall.jlu.edu.cn/',
                          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'})
        s.verify = False

        print('正在登录...')
        r = s.get('https://ehall.jlu.edu.cn/jlu_portal/login', timeout=TIMEOUT)
        pid = re.search('(?<=name="pid" value=")[a-z0-9]{8}', r.text)[0]
        log.debug(f"PID: {pid}")
        postPayload = {'username': username, 'password': password, 'pid': pid}
        r = s.post('https://ehall.jlu.edu.cn/sso/login', data=postPayload, timeout=TIMEOUT)

        print('正在请求打卡数据...')
        r = s.get(f"https://ehall.jlu.edu.cn/infoplus/form/BKSMRDK/start", timeout=TIMEOUT)
        csrfToken = re.search('(?<=csrfToken" content=").{32}', r.text)[0]
        postPayload = {'idc': 'BKSMRDK', 'csrfToken': csrfToken}
        r = s.post('https://ehall.jlu.edu.cn/infoplus/interface/start', data=postPayload, timeout=TIMEOUT)
        sid = re.search('(?<=form/)\\d*(?=/render)', r.text)[0]
        postPayload = {'stepId': sid, 'csrfToken': csrfToken}
        r = s.post('https://ehall.jlu.edu.cn/infoplus/interface/render', data=postPayload, timeout=TIMEOUT)
        data = json.loads(r.content)['entities'][0]

        print('提交打卡信息中...')
        for k, v in fields.items():
            if eval(conditions.get(k, 'True')):
                data['data'][k] = v
        postPayload = {
            'actionId': 1,
            'formData': json.dumps(data['data']),
            'nextUsers': '{}',
            'stepId': sid,
            'timestamp': int(time()),
            'boundFields': ','.join(data['fields'].keys()),
            'csrfToken': csrfToken
        }
        r = s.post('https://ehall.jlu.edu.cn/infoplus/interface/doAction', data=postPayload, timeout=TIMEOUT)
        if json.loads(r.content)['ecode'] != 'SUCCEED':
            raise Exception('打卡失败，请重试')
        print('打卡成功!')
    except Exception as e:
        log.error('打卡失败')
        log.error(e)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log.warning('开始打卡.')

def main_handler(task, args):
    punchcard('qianmz1718', '13931763095qmz')
