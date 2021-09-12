import re
from lxml import etree
from ics import Calendar, Event


def getEvent(date, course,year):
    # name=None, begin=None, end=None, duration=None, uid=None, description=None, created=None, last_modified=None, location=None, url=None,
    # transparent=None,alarms=None, attendees=None, categories=None, status=None, organizer=None, geo=None, classification=None
    e = Event()
    e.name = course[0]

    # '2014-01-01 00:00:00'
    date = date[1]
    day, month = re.findall('(\d+) (\d+) ', date)[0]
    day = '0' + day if len(day) == 1 else int(day)
    month = '0' + month if len(month) == 1 else int(month)

    begin_time, end_time = re.findall('(\d+:\d+[上下]午) - (\d+:\d+[上下]午)', course[3])[0]
    f1 = True if '上午' in begin_time else False
    begin_time = re.findall('(\d+:\d+)', begin_time)[0]
    begin_time = begin_time.split(':')
    begin_time = ['{:0>2d}'.format(int(b)) for b in begin_time]
    begin_time = begin_time[0] + ':' + begin_time[1] if f1 else str(int(begin_time[0]) + 12) + ':' + begin_time[1]

    f2 = True if '上午' in end_time else False
    end_time = re.findall('(\d+:\d+)', end_time)[0]
    end_time = end_time.split(':')
    end_time = ['{:0>2d}'.format(int(b)) for b in end_time]
    end_time = end_time[0] + ':' + end_time[1] if f2 else str(int(end_time[0]) + 12) + ':' + end_time[1]

    e.begin = f'{year}-{month}-{day} {begin_time}:00'
    e.end = f'{year}-{month}-{day} {end_time}:00'
    # print(course)
    # print(e.begin,e.end)
    e.location = course[4]
    e.description = course[1] + course[2]
    # e.organizer = ''
    if '员工' in course[5]:
        e.description +='\n员工'
    else:
        for i in range(6, len(course)):
            e.description += '\n'+course[i]
    return e


if __name__ == '__main__':
    with open('./我的每周课程表_files/SA_LEARNER_SERVICES.SSR_SSENRL_SCHD_W.html', 'r', encoding='utf8')as f:
        html = f.read()
    html = etree.HTML(html)

    date = html.xpath('//*[@id="WEEKLY_SCHED_HTMLAREA"]/tbody/tr[1]/th')[1:]
    date_list = []
    for data in date:
        str_t = etree.tostring(data)
        html_t = etree.HTML(str_t)
        data = html_t.xpath('//text()')
        data = [d.replace('\n', '') for d in data]
        date_list.append(data)

    table = []
    for i in range(49):
        table.append([])
        for j in range(8):
            table[i].append(None)
    trs = html.xpath('//*[@id="WEEKLY_SCHED_HTMLAREA"]/tbody/tr')[1:]
    year=html.xpath('//*[@id="win0divDERIVED_CLASS_S_DESCR100_2"]/table/tbody/tr[1]/td/text()')[0]
    year=int(re.findall('(\d+) - ',year)[0])


    for i in range(49):
        str_tr = etree.tostring(trs[i])
        html_tr = etree.HTML(str_tr)
        tds = html_tr.xpath('//td')
        offset = 0
        for j in range(8):
            str_td = etree.tostring(tds[j-offset])
            html_td = etree.HTML(str_td)
            try:
                rows = html_td.xpath('//@rowspan')[0]
                rows = int(rows)
            except:
                rows = 1


            if i == 0:
                table[i][j] = [html_td.xpath('//text()'), rows, 1]
                # table[i][j] = [1, rows]
            else:
                if table[i - 1][j] and table[i - 1][j][0] and table[i - 1][j][1] > 1:
                    offset += 1
                    table[i][j] = [table[i - 1][j][0], table[i - 1][j][1] - 1, 0]
                else:
                    table[i][j] = [html_td.xpath('//text()'), rows, 1]

        # print(table[i])


    c = Calendar()
    for i in range(49):
        for j in range(8):
            if j==0:
                continue
            if not table[i][j] or table[i][j][2] == 0:
                continue
            course = table[i][j][0]
            try:
                if course == [] or course == ['\xa0'] or len(course) < 5:
                    continue
            except Exception as e:
                print(i, j, e)
            # print(date_list[j - 2], i)
            # print(course)
            e = getEvent(date_list[j-1], course,year)
            c.events.add(e)

    # input()
    with open('tmp.ics', 'w', encoding='utf-8')as f:
        f.write(str(c))
    content = ''
    with open('tmp.ics', 'r', encoding='utf8')as f:
        for line in f.readlines():
            if 'DTEND' in line or 'DTSTART' in line:
                line = line.replace('Z', '')
            if line == '\n':
                continue
            content += line
    with open('my.ics', 'w', encoding='utf-8')as f:
        f.write(content)
