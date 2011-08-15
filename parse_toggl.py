#!/usr/bin/env python
from datetime import datetime
from xlwt import Borders, Pattern, Workbook, XFStyle
import base64
import calendar
import os
import simplejson
import urllib
import urllib2

API_KEY = '23172de359835c06c4d5f1b7dfbea85a'
EXCEL_DATE_FMT = '%m/%d/%Y'

TEST = True

def load_from_test_file():
    file = open('time_entries.json')
    json = simplejson.load(file)
    file.close()
    return json

def load_from_toggl():
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

    json = simplejson.load(resp)
    return json

def build_totals(data):
    """Collect data into a date/task/hours structure for further processing
    """
    totals = {}
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
    return totals

def write_excel(totals):
    """Write out the collected totals to an excel file
    """
    workbook = Workbook()
    worksheet = workbook.add_sheet('New Sheet')

    data_cell = XFStyle()
    data_cell.borders.top = Borders.THIN
    data_cell.borders.top_colour = 0
    data_cell.borders.bottom = Borders.THIN
    data_cell.borders.bottom_colour = 0
    data_cell.borders.left = Borders.THIN
    data_cell.borders.left_colour = 0
    data_cell.borders.right = Borders.THIN
    data_cell.borders.right_colour = 0

    header = XFStyle()
    header.borders = data_cell.borders
    header.font.colour_index = 1
    header.pattern.pattern = Pattern.SOLID_PATTERN
    header.pattern.pattern_fore_colour = 18

    daily_totals_title = XFStyle()
    daily_totals_title.borders = data_cell.borders
    daily_totals_title.font.colour_index = 1
    daily_totals_title.pattern.pattern = Pattern.SOLID_PATTERN
    daily_totals_title.pattern.pattern_fore_colour = 16

    daily_totals_footer = XFStyle()
    daily_totals_footer.borders = data_cell.borders
    daily_totals_footer.font.italic = 1

    bimonthly_total_header = XFStyle()
    bimonthly_total_header.borders = data_cell.borders
    bimonthly_total_header.font.bold = 1
    bimonthly_total_header.font.colour_index = 1
    bimonthly_total_header.pattern.pattern = Pattern.SOLID_PATTERN
    bimonthly_total_header.pattern.pattern_fore_colour = 16

    # write the header for the first block
    descriptions = []
    daily_totals = []
    task_totals = []

    worksheet.write(0, 0, 'Description of Activity', header)

    max_description_len = 0
    for j, date in enumerate(sorted(totals.iterkeys())):
        row_offset = 0
        if datetime.strptime(date, EXCEL_DATE_FMT).day > 15:
            # by this point we should have processed everything in the first
            # block so we'll now start processing deeper entries
            row_offset = len(descriptions) + 4

        worksheet.write(row_offset, j + 1, date, header)
        daily_totals.append(0)

        for desc in totals[date]:
            if desc not in descriptions:
                descriptions.append(desc)
                task_totals.append(0)
                worksheet.write(row_offset + len(descriptions), 0, desc, data_cell)
                max_description_len = max(len(desc), max_description_len)

            i = descriptions.index(desc)
            hours = totals[date][desc]
            worksheet.write(row_offset + i + 1, j + 1, hours)
            daily_totals[j] += hours
            task_totals[i] += hours

    # write the last column
    daily_totals_len = len(daily_totals) + 1
    worksheet.write(row_offset, daily_totals_len, 'Bi-Monthly Total', bimonthly_total_header)
    
    # set the first and last column widths for readability
    worksheet.col(0).width = max_description_len * 256
    worksheet.col(daily_totals_len).width = len('Bi-Monthly Total') * 256

    # write out the task totals as a columns
    for i, task_total in enumerate(task_totals):
        worksheet.write(row_offset + i + 1, daily_totals_len, task_total, data_cell)

    # write out the daily totals as a row
    last_row = len(descriptions) + 1
    block_total = 0
    worksheet.write(row_offset + last_row, 0, 'Daily Totals', daily_totals_title)

    for i, daily_total in enumerate(daily_totals):
        worksheet.write(row_offset + last_row, i + 1, daily_total, daily_totals_footer)
        block_total += daily_total

    worksheet.write(row_offset + last_row, daily_totals_len, block_total, data_cell)

    # save the file to disk
    curpath = os.path.dirname(__file__)
    workbook.save(os.path.join(curpath, 'test.xls'))

def main():
    """Main controller of processing. Reads in information from toggl, writes
    out to an Excel file then emails the file to Michelle.
    """
    
    results = None
    if (TEST):
        results = load_from_test_file()
    else:
        results = load_from_toggl()

    totals = build_totals(results['data'])
    write_excel(totals)

if __name__ == '__main__':
    main()
