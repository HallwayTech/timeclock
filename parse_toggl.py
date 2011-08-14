#!/usr/bin/env python
from datetime import datetime
from pyExcelerator import Font, Pattern, Workbook, XFStyle
import base64
import calendar
import os
import simplejson
import urllib
import urllib2

API_KEY = '23172de359835c06c4d5f1b7dfbea85a'
EXCEL_DATE_FMT = '%m/%d/%Y'

def write_excel(totals):
    workbook = Workbook()
    worksheet = workbook.add_sheet('New Sheet')

    blue_bg = XFStyle()
    blue_bg.font.colour_index = 1
    blue_bg.pattern.pattern = Pattern.SOLID_PATTERN
    blue_bg.pattern.pattern_fore_colour = 18

    red_bg = XFStyle()
    red_bg.font.colour_index = 1
    red_bg.pattern.pattern = Pattern.SOLID_PATTERN
    red_bg.pattern.pattern_fore_colour = 16

    bimonthly_total_header = XFStyle()
    bimonthly_total_header.font.bold = 1
    bimonthly_total_header.font.colour_index = 1
    bimonthly_total_header.pattern.pattern = Pattern.SOLID_PATTERN
    bimonthly_total_header.pattern.pattern_fore_colour = 16

    daily_totals_footer = XFStyle()
    daily_totals_footer.font.italic = 1

    # write the header for the first block
    descriptions = []
    daily_totals = []
    task_totals = []
    
    worksheet.write(0, 0, 'Description of Activity', blue_bg)

    for j, date in enumerate(sorted(totals.iterkeys())):
        if datetime.strptime(date, EXCEL_DATE_FMT).day > 15:
            break
        worksheet.write(0, j + 1, date, blue_bg)
        daily_totals.append(0)

        for desc in totals[date]:
            if desc not in descriptions:
                descriptions.append(desc)
                task_totals.append(0)
                worksheet.write(len(descriptions), 0, desc)

            i = descriptions.index(desc)
            hours = totals[date][desc]
            worksheet.write(i + 1, j + 1, hours)
            daily_totals[j] += hours
            task_totals[i] += hours

    # write the last column
    daily_totals_len = len(daily_totals) + 1
    worksheet.write(0, daily_totals_len, 'Bi-Monthly Total', bimonthly_total_header)

    for i, task_total in enumerate(task_totals):
        worksheet.write(i + 1, daily_totals_len, task_total)

    # write the last row
    last_row = len(descriptions) + 1
    block_total = 0
    worksheet.write(last_row, 0, 'Daily Totals', red_bg)

    for i, daily_total in enumerate(daily_totals):
        worksheet.write(last_row, i + 1, daily_total, daily_totals_footer)
        block_total += daily_total

    worksheet.write(last_row, daily_totals_len, block_total)
    curpath = os.path.dirname(__file__)
    workbook.save(os.path.join(curpath, 'test.xls'))

def main():
    current_month = datetime.strftime(datetime.today(), '%m')

    # find out what month to report. default to the current month
    month = raw_input('Enter the month you want to report [%s]: ' % (current_month))
    if len(month) == 0:
        month = current_month

    # make sure we have a two character month
    while len(month) < 2:
        month = '0' + month

    start_date = datetime.today()
    monthrange = calendar.monthrange(start_date.year, start_date.month)
    data = {'start_date': '%s-01' % (datetime.strftime(start_date, '%Y-%m')),
            'end_date': '%s-%s' % (datetime.strftime(start_date, '%Y-%m'), monthrange[1])}
    print data

    # hit toggl for the time entries
    req = urllib2.Request('https://www.toggl.com/api/v6/time_entries.json?' + urllib.urlencode(data))
    authn_header = base64.encodestring('%s:api_token' % API_KEY)
    req.add_header('Authorization', 'Basic %s' % authn_header)
    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError, msg:
        print "Error loading time entries from toggl: %s" % (msg)
        exit(1)

    result = simplejson.load(resp)
    data = result['data']
    totals = {}
    total_hours = 0

    for d in data:
        date = datetime.strftime(datetime.strptime(d['start'][:10], "%Y-%m-%d"), EXCEL_DATE_FMT)
        day = {}
        if date in totals:
            day = totals[date]

        hours = 0
        desc = d['description']
        if desc in day:
            hours = day[desc]

        day[desc] = hours + (d['duration'] / 3600)
        totals[date] = day

        total_hours += day[desc]

    write_excel(totals)

if __name__ == '__main__':
    main()
