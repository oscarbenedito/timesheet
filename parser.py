#!/usr/bin/env python3

# Copyright (C) 2020 Oscar Benedito <oscar@oscarbenedito.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import re
import datetime


class Task:
    def __init__(self, description, tags):
        self.intervals = list()
        self.description = description
        self.tags = tags

    def __repr__(self):
        return 'Task({}, {}, {})'.format(self.intervals, self.description,
                                         self.tags)

    def id(self):
        if len(self.intervals) == 0:
            raise ValueError('Task has never been started. It needs a starting '
                             'date to have an ID.')
        return self.intervals[0][0].strftime('%Y%m%d%H%M%S')

    def is_open(self):
        return len(self.intervals) > 0 and self.intervals[-1][1] is None

    def stop(self, time):
        if not self.is_open():
            raise ValueError('Task is already stopped.')

        self.intervals[-1][1] = time

    def start(self, time):
        if self.is_open():
            raise ValueError('Task is already started.')

        self.intervals.append([time, None])


class TimeTracker:
    re_day  = re.compile(r'^(\d\d\d\d)-(\d\d)-(\d\d):(?:[ \t]+#[ \t].*)?$')
    re_new  = re.compile(r'^(\d\d)(\d\d)(\d\d)?[ \t]+(.+?)(?:[ \t]+#[ \t].*)?$')
    re_stop = re.compile(r'^(\d\d)(\d\d)(\d\d)?\.(?:[ \t]+#[ \t].*)?$')
    re_rel  = re.compile(r'^(\d\d)(\d\d)(\d\d)?(\^+)(?:[ \t]+#[ \t].*)?$')
    re_abs  = re.compile(r'^(\d\d)(\d\d)(\d\d)?\^(?:(\d\d\d\d)-(\d\d)-(\d\d)T)?'
                         '(\d\d)(\d\d)(\d\d)?(?:[ \t]+#[ \t].*)?$')
    re_tag  = re.compile(r'[ \t]#[a-zA-Z0-9_]+(?=[ \t])')

    def __init__(self):
        self.tasks = dict()
        self.c_dt = None            # current datetime
        self.c_task = None          # current task
        self.l_task = None          # last task
        self.day_is_empty = None    # true if there are tasks on the current day

    def stop_task(self):
        if self.c_task is not None and self.c_task.is_open():
            self.c_task.stop(self.c_dt)
            return True

        return False

    def start_task(self, task):
        if task != self.c_task:
            self.l_task = self.c_task
            self.c_task = task

        self.c_task.start(self.c_dt)

    def process_line(self, line):
        line.strip()
        if len(line) == 0 or line[:2] == '# ' or line[:2] == '#\t':
            # whitespace/comment
            return

        if len(line) < 5 or (line[4].isdigit() and len(line) < 7):
            raise ValueError('Incorrect syntax.')

        if line[4] == '-':
            # day change
            self.process_line_day_change(line)
            return

        # depending on time precission (seconds or minutes)
        i = 6 if line[4].isdigit() else 4

        if line[i] == ' ' or line[i] == '\t':
            # start new task
            self.process_line_new_task(line)
            return

        if line[i] == '.':
            # stop task
            self.process_line_stop_task(line)
            return

        if line[i] == '^' and len(line) > i+1 and line[i+1].isdigit():
            # continue task by time stamp
            self.proces_line_continue_time(line)
            return

        # continue last task
        self.process_line_continue_last(line)

    def process_datetime(self, hour, minute, second):
        if self.c_dt is None:
            raise ValueError('Task initialized before day declaration.')

        hour = int(hour)
        minute = int(minute)
        second = int(second) if second is not None else 0
        date = self.c_dt.replace(hour=hour, minute=minute, second=second)

        if date < self.c_dt or (date == self.c_dt and not self.day_is_empty):
            raise ValueError('Tasks are not in chronological order or have the '
                             'same starting time.')

        self.c_dt = date
        self.day_is_empty = False

    def process_line_day_change(self, line):
        m = self.re_day.search(line)
        if m is None:
            raise ValueError('Incorrect syntax.')

        date = datetime.datetime(int(m[1]), int(m[2]), int(m[3]))

        if self.c_dt is not None and date <= self.c_dt:
            raise ValueError('New date is older than last recorded time.')

        self.c_dt = date
        self.day_is_empty = True

    def process_line_new_task(self, line):
        m = self.re_new.search(line)
        if m is None:
            raise ValueError('Incorrect syntax.')

        self.process_datetime(m[1], m[2], m[3])

        description = m[4]
        tags = set()
        for m_tag in self.re_tag.finditer(description):
            tags.add(m_tag[2])
        description = self.re_tag.sub('', description).strip()

        task = Task(description, tags)

        self.stop_task()
        self.start_task(task)

        self.tasks[task.id()] = task

    def process_line_stop_task(self, line):
        m = self.re_stop.search(line)
        if m is None:
            raise ValueError('Incorrect syntax.')

        self.process_datetime(m[1], m[2], m[3])

        if not self.stop_task():
            raise ValueError('No task to stop.')

    def proces_line_continue_time(self, line):
        m = self.re_abs.search(line)
        if m is None:
            raise ValueError('Incorrect syntax.')

        self.process_datetime(m[1], m[2], m[3])

        iden = self.c_dt.strftime('%Y%m%d') if m[4] is None else m[4]+m[5]+m[6]
        iden += m[7] + m[8]
        iden += m[9] if m[9] is not None else '00'

        n_task = self.tasks.get(iden)
        if n_task is None:
            pretty_date = '{}-{}-{} {}:{}:{}'.format(iden[:4], iden[4:6],
                                                     iden[6:8], iden[8:10],
                                                     iden[10:12], iden[12:14])
            raise ValueError('No task started on {}.'.format(pretty_date))

        self.stop_task()
        self.start_task(n_task)

    def process_line_continue_last(self, line):
        m = self.re_rel.search(line)
        if m is None:
            raise ValueError('Incorrect syntax.')

        self.process_datetime(m[1], m[2], m[3])

        n_task = self.l_task if self.stop_task() else self.c_task
        if n_task is None:
            raise ValueError('No task to resume.')

        self.stop_task()
        self.start_task(n_task)


def main():
    if len(sys.argv) != 2:
        print('This program takes one argument (the file with the data).')
        exit(1)

    with open(sys.argv[1], 'r') as f:
        lines = f.read().splitlines()

    tt = TimeTracker()
    for i, line in enumerate(lines):
        try:
            tt.process_line(line)
        except ValueError as e:
            print('Error on line {}: {}'.format(i+1, e))
            exit(1)

    print(tt.tasks)


if __name__ == "__main__":
    main()
