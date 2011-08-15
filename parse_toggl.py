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

TEST = False

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

summary_total_header = XFStyle()
summary_total_header.borders = data_cell.borders
summary_total_header.font.bold = 1
summary_total_header.font.colour_index = 1
summary_total_header.pattern.pattern = Pattern.SOLID_PATTERN
summary_total_header.pattern.pattern_fore_colour = 16

def load_from_test_file():
    """Loads a file for test data
    """
    file = open('time_entries.json')
    json = simplejson.load(file)
    file.close()
    return json

def load_from_toggl():
    """Load live data from toggl
    """
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

def write_time_block(worksheet, totals, row_offset=0, first_block=True):
    if (row_offset > 0):
        row_offset += 3
    descriptions = []
    daily_totals = []
    task_totals = []
    total_hours = 0
    max_description_len = 0

    for date in sorted(totals.iterkeys()):
        if first_block and datetime.strptime(date, EXCEL_DATE_FMT).day > 15:
            break
        elif not first_block and datetime.strptime(date, EXCEL_DATE_FMT).day <= 15:
            continue

        daily_totals.append(0)
        worksheet.write(row_offset, len(daily_totals), date, header)

        for desc in totals[date]:
            if desc not in descriptions:
                descriptions.append(desc)
                task_totals.append(0)
                worksheet.write(row_offset + len(descriptions), 0, desc, data_cell)
                max_description_len = max(len(desc), max_description_len)

            i = descriptions.index(desc)
            hours = totals[date][desc]
            worksheet.write(row_offset + i + 1, len(daily_totals), hours)

            # add the hours to the daily, task and total counters
            daily_totals[len(daily_totals) - 1] += hours
            task_totals[i] += hours
            total_hours += hours

    worksheet.write(row_offset, 0, 'Description of Activity', header)
    worksheet.row(row_offset).height = 350

    # write the last column
    daily_totals_len = len(daily_totals) + 1
    worksheet.write(row_offset, daily_totals_len, 'Bi-Monthly Total', summary_total_header)

    # set the first and last column widths for readability
    if max_description_len > 0:
        worksheet.col(0).width = max_description_len * 256
    worksheet.col(daily_totals_len).width = len('Bi-Monthly Total') * 256

    last_row = len(descriptions) + 1
    # write out the task totals as a column
    for i, task_total in enumerate(task_totals):
        worksheet.write(row_offset + i + 1, daily_totals_len, task_total, data_cell)

    # write out the daily totals as a row
    worksheet.write(row_offset + last_row, 0, 'Daily Totals', daily_totals_title)
    worksheet.row(row_offset + last_row).height = 300
    for i, daily_total in enumerate(daily_totals):
        worksheet.write(row_offset + last_row, i + 1, daily_total, data_cell)

    # write out the summed total of tasks for this block
    worksheet.write(row_offset + last_row, daily_totals_len, total_hours, data_cell)

    return len(descriptions), total_hours

def write_excel(totals):
    """Write out the collected totals to an excel file
    """
    workbook = Workbook()
    worksheet = workbook.add_sheet('New Sheet')

    # write the header for the first block
    total_hours = 0
    total_tasks = 0

    block_tasks, block_total = write_time_block(worksheet, totals)
    total_hours += block_total
    total_tasks += block_tasks

    block_tasks, block_total = write_time_block(worksheet, totals, block_tasks, False)
    total_hours += block_total
    total_tasks += block_tasks

    # write out the total hours
    worksheet.write(total_tasks + 6, 0, 'Monthly Total', summary_total_header)
    worksheet.write(total_tasks + 6, 1, total_hours, data_cell)

    # write out the user and date
    name = raw_input('Who is this report for? ')
    worksheet.write(total_tasks + 8, 0, 'Name: %s' % (name))
    worksheet.write(total_tasks + 9, 0, 'Date: %s' % (datetime.strftime(datetime.today(), '%m/%d/%Y')))

    # write the signature field
    worksheet.write(total_tasks + 8, 6, 'Signature:')
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
