import os
import time
import logging

import viperdriver
from viperdriver import SessionDriver

logger = viperdriver.logger # this is enough

SLEEP = 3600
SLEEP_MIN = 900

if __debug__:
    viperdriver.loggers_set(logging.DEBUG)

SITES = { \
    'jh': 'https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6',\
    'wm': 'https://www.worldometers.info/coronavirus/' \
    }

def info_collect(sites):
    complete_info = {}
    drv = pom()
    for site in SITES:
        complete_info.update({site: drv.info_get(site, SITES[site])})
    drv.quit()
    return complete_info

def alert_wm(info):
    txt = ''
    info.pop('As of')
    i_deaths = int(info['Deaths'].replace(',',''))
    i_cases = int(info['Cases'].replace(',',''))
    rate = round( i_deaths / i_cases, 4)  * 100
    info['Deaths'] += '(' + str(rate) + '%)'
    for i in info:
        txt += i + ': ' + info[i] + '\n'
    txt = list(txt)
    txt = ''.join(txt)
    txt = txt.replace('As of: ', '')
    return txt

def alert_compose(info):
    for site in info:
        if site == 'wm':
            return alert_wm(info[site])

def output(stats, timestamp):
    if __debug__:
        logger.debug(stats + '\n' + timestamp)
    else:
        cmd = 'osascript -e \'display notification \"' + stats + '\" with title \"Wuhan Virus Update ' + timestamp + '\"\''
        os.system(cmd)

class pom(SessionDriver):

    def __init__(self):
        super().__init__()
        # if in debug mode, make sure new session is created first
        self.launch(not __debug__) # will attempt to connect to existing sesssion if debug mode
        self.refresh() # do not remove, required if connected to existing session

    def __enter__(self):
        pass

    def info_get(self, alias, url):
        self.get(url)
        if alias == 'wm':
            return self.__info_get_wm__()
        if alias == 'jh':
            return self.__info_get_jh__()

    def __info_get_wm__(self):
        elems = self.find_elements_by_xpath('//div[@class=\'maincounter-number\']/span')
        cases = elems[0].text
        deaths = elems[1].text
        last_updated = self.find_elements_by_xpath('//div[@class=\'content-inner\']/div')[1].text
        critical_abs = self.find_elements_by_class_name('number-table')[1].text
        critical_percent = self.find_element_by_xpath('//div[@style=\'float:right; text-align:center\']/strong').text
        critical = critical_abs + '(' + critical_percent + '%)'
        return {'Cases': cases, 'Deaths': deaths, 'Critical': critical, 'As of': last_updated.split(': ')[1], }

    def __info_get_jh__(self):
        return {'TO BE DEVELOPED'}

    def quit(self):
        if not __debug__:
            super().quit()

    def __exit__(self, exception_type, exception_value, traceback):
        if not __debug__:
            self.quit()

def main():

    if SLEEP < SLEEP_MIN: # to restrict polling period in order not to abuse the sources
        logger.info('Polling period may not be less than ' + SLEEP_MIN + ' min.')
        raise SystemExit

    prev = ''

    # init_browser()

    while True:
        info = info_collect(SITES)
        last = info['wm']['As of']
        if  prev < last:
            output(alert_compose(info), last)
        prev = last
        if __debug__:
            logger.debug('Exiting due to debug mode.')
            break
        time.sleep(SLEEP)

if __name__ == '__main__':
    main()
