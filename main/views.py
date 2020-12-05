import flask
from main import app
import os
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import jaconv


@app.route('/')  # ホーム
def corona():
    return flask.render_template('index.html', update_time=update_time)


def text_int(overseas_table_data):
    Fnum = overseas_table_data.split('名')[0]
    Fnum = Fnum.replace(',', "")
    return int(Fnum.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)})))


links = []
titles = []


def get_links():
    global links
    global titles
    html_doc = requests.get(
        'https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000121431_00086.html').content
    soup = BeautifulSoup(html_doc, 'html.parser')
    a_tags = soup.find_all('a')
    titles.clear()
    links.clear()
    for a in a_tags:
        if "新型コロナウイルス感染症の現在の状況と厚生労働省の対応について" in a.text:
            link = a.get('href')
            links.append(link)
            titles.append(a.text)
            # print(link)
    return links


one_corona_overseas = []
all_corona_overseas = {}


def overseas_transition():
    global links
    global all_corona_overseas
    global dates
    date_number = 0
    all_corona_overseas.clear()
    for link in links:
        tables = get_tables(link)
        # title = get_title(link)
        # get_title()
        for table in tables:
            table_trs = table.find_all('tr')
            one_corona_overseas = []
            for tr_number, tr in enumerate(table_trs):
                table_tds = tr.find_all("td")
                table_th = tr.find_all("th")
                if tr_number == 0:
                    table_columns = [td.text for td in table_tds]
                    table_ths = [th.text for th in table_th]
                    table_columns.extend(table_ths)
                    if '国・地域' in table_columns[0] and '感染者' in table_columns[1] and '死亡者' in table_columns[2]:
                        pass
                    else:
                        break
                else:
                    try:
                        table_data = [td.text for td in table_tds]
                        table_data.insert(0, "")  # 配列の長さを合わせる
                        if '国・地域' in table_columns[0] and '感染者' in table_columns[1] and '死亡者' in table_columns[2]:
                            table_data[2] = text_int(table_data[2])
                            table_data[3] = text_int(table_data[3])
                            one_corona_overseas.append(table_data)
                        else:
                            one_corona_overseas.append(table_data)
                    except:
                        pass
            else:
                all_corona_overseas[dates[date_number]] = one_corona_overseas
        else:
            date_number = date_number + 1
    else:
        all_overseas_json_path = os.path.abspath(
            __file__)[:-9] + "/static/data/all_corona_overseas.json"
        # JSON ファイルへの書き込み
        # print(all_corona_overseas)
        with open(all_overseas_json_path, 'w') as f:
            json.dump(all_corona_overseas, f)


# get_links()
def get_tables(link):
    # global links
    smoll_html = requests.get(link).content
    soup = BeautifulSoup(smoll_html, 'html.parser')
    return soup.find_all('table')


dates = []


def get_title():
    global titles
    global dates
    dates.clear()
    for title in titles:
        title = title.split('年')[1]
        month = title.split('月')[0]
        day = title.split('月')[1].split('日')[0]
        month = jaconv.z2h(month, digit=True, ascii=True)
        day = jaconv.z2h(day, digit=True, ascii=True)
        date = month + '/' + day
        dates.append(date)


corona_data = []
corona_overseas = []
update_time, latest_link, latest_date = None, None, None


def create_list():
    global update_time
    global links
    global latest_link
    global corona_overseas
    links = get_links()
    get_title()
    tables = get_tables(links[0])
    if links[0] == latest_link:
        print("no change data")
        return
    else:
        latest_date = dates[0]
        # overseas_transition()
        latest_link = links[0]
        # print(latest_link)
        update_time = time.strftime("%Y/%m/%d %H:%M")
        corona_data.clear()
        corona_overseas.clear()
        for table in tables:
            table_trs = table.find_all('tr')
            for tr_number, tr in enumerate(table_trs):
                table_tds = tr.find_all("td")
                if tr_number == 0:
                    table_columns = [td.text for td in table_tds]
                    # print(table_columns)
                    if '国・地域' in table_columns and '感染者' in table_columns and '死亡者' in table_columns:
                        # print(table_columns)
                        pass
                    elif '居住地' in table_columns and 'チャーター便' not in table_columns:
                        # print(table_columns)
                        pass
                    else:
                        # print(table_columns, 'pass')
                        break
                else:
                    try:
                        table_data = [td.text for td in table_tds]
                        # print(table_data)
                        table_data.insert(0, "")  # 配列の長さを合わせる
                        # print(table_data)
                        if '国・地域' in table_columns and '感染者' in table_columns and '死亡者' in table_columns:
                            table_data[2] = text_int(table_data[2])
                            table_data[3] = text_int(table_data[3])
                            corona_overseas.append(table_data)
                            # print(table_data)
                        else:
                            corona_data.append(table_data)
                    except:
                        pass
        else:
            japan_json_path = os.path.abspath(
                __file__)[:-9] + "/static/data/corona_data.json"
            overseas_json_path = os.path.abspath(
                __file__)[:-9] + "/static/data/corona_overseas.json"
            # JSON ファイルへの書き込み
            with open(japan_json_path, 'w') as f:
                json.dump(corona_data, f)

            with open(overseas_json_path, 'w') as f:
                json.dump(corona_overseas, f)

            if latest_date in all_corona_overseas:
                all_corona_overseas[latest_date] = corona_overseas
                all_overseas_json_path = os.path.abspath(
                    __file__)[:-9] + "/static/data/all_corona_overseas.json"
                # print(all_corona_overseas)
                with open(all_overseas_json_path, 'w') as f:
                    json.dump(all_corona_overseas, f)

# create_list()

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=create_list, trigger="interval", hours=18)
# scheduler.start()

# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())
