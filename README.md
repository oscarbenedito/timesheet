# Timesheet file format

The goal of this project is to define a file format that allows the user to
record the time spent on tasks (a timesheet). The design is inspired by Tim
Weber's [timesheet.txt][ts].

## Motivation

The motivation behind this project is personal usage. I wanted to be able to
track time easily in a system that was durable. This project pretends to specify
a file format that is easy to parse (by a machine) and read (by a human).

The requirements to work with such format should only be access to a text
editor, although there will be a script that lets the user view and edit such a
file from the command line.

Why plain text? Because it is easy to read and write, and you don't need any
special program to access your data. On top of that, it is easy to parse, so
anyone a bit familiar with programming will be able to create a parser that
works exactly how they want. Even if you don't, hopefully my parser is easy to
understand, and it should take an interested user less than half an hour to get
familiar with the code.

## Specification

A bit more formally. In a timesheet file, each line fits in one of the following
categories:

- Whitespace: blank line or line with whitespace characters only.
- Date change: a line that specifies a change in the date. Format:
  `YYYY-MM-DD:`.
- Task change: a change in the current task. This lines can be divided in the
  following subcategories:
  - Start task: stop last task and start a new one. Format: `HHMM[SS]
    description`.
  - Stop task: stop current task. Format: `HHMM[SS].`.
  - Continue last task: continue the task previous to the current one (see
    examples). Format: `HHMM[SS]^`.
  - Continue task by start time: continue a task specifying it's start time.
    Format: `HHMM[SS]^[YYYY-DD-MMT]HHMM[SS]`.

The definition of the format symbols:

- On the date change, `YYYY`, `MM` and `DD` stand for the year, month and day,
  respectively.
- On task changes, `HH`, `MM` and `SS` stand for hour, minute and second,
  respectively. Note that on the subcategory "continue task by start time", the
  `T` represents the character `T`, not a variable.
- Square brackets (`[`, `]`) delimit an optional value.
- `description` is a task description. It is a non-empty string without a
  newline or a `#` character surrounded by whitespace. Any word started with the
  `#` character is considered a tag for the task, and should not be considered
  part of the description message, a description doesn't need to have any other
  text if it already has a tag, a tag must only contain letters (lowercase or
  uppercase), numbers and underscores.
- A space (` `) stands for non-zero amount of spaces and/or tabs.
- Any other character stands for the literal value of the character.

On top of that, any line can start and/or end with any amount of spaces and/or
tabs (which should be ignored by the parser). Any line can have comments at the
end, which start with a `#` surrounded by spaces (or end of line characters) and
end at the end of the line.

When parsing the description of a task, tags will be substituted by a space in
the description, and then any leading or trailing spaces will be deleted.
Therefore, any tags appearing at the start or end of the description will be
completely deleted, while tags in between description text will be substituted
by a space.

All entries must be in chronological order and there must not be two entries
starting at the same time. If no second is specified for the start time of a
task, the default value is 0.

If no day is specified when continuing a task by start time, then the current
day is used (the day specified on last date change).

### Examples

An example of a file would be:

```
TODO
```

## Note

I hope to end up with a file without any ambiguities. If you have a question
that is not answered, please [contact me][c] or open an issue.

## TODO

- License
- Examples

[ts]: <https://github.com/scy/timesheet.txt>
[c]: <https://oscarbenedito.com/contact/>
