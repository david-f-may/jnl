# jnl.py

## Getting started

jnl is a command-line application following the spirit of bullet journaling as
detailed in the Bullet Journal method by Ryder Carroll. It is written in
Python,
and is a simple application at its core.

To start using jnl, you need to initialize the journal file, which is
essentially a SQLite database file.

```
python3.11 jnl main.jnl
Created journal file main.jnl
```

This will create a SQLite database file called main.jnl and get it ready for
holding your journal data. Any command will initialize the jnl file, but will
not do anything else if the file doesn't exist. It is probably just as easy
to provide the jnl command with the name of the database file to initialize
it.

Once you create the jnl file, you can use

```
jnl main.jnl --help
```

to get a summary of the commands supported by the jnl program.

## Using jnl

When the jnl file is initialized, you can enter commands to populate the
journal file. For example, you can enter a log.

```
jnl main.jnl --add --log "took M3 and Noah to Sadies"
```

In Ryder's Bullet journal method, a log is an entry that states what is
happening in your life or something you did. In the above log, I indicate that
I took my wife and son to a restaurant. A great deal of your life can be
detailed using logs.

After the above entry, you can get a listing of what is in the journal file
with

```
jnl main.jnl --ls
** TYPE ** : ** PAGE ** : ** ITEM_ID ** : ** CREATED ** : ** UPDATED ** : **
ITEM **

*** Logs, ideas, quotes, notes ***

• : — : 2: 2023-11-23 19:22:16: None | took M3 and Noah to Sadies

*** Completed todos ***

*** No completed todo items ***

*** Open todos ***

*** No open todo items ***
```

This looks a little intimidating, so let's step through it. The first line
shows
you what the fields are in each entry. In this case, the log is given by a •
as
the type. Other types are ideas (☼), notes (❃), quotes (”) and todos
(open todo = ✓, completed todo = ✗). We will talk about todos more later.

The next field (after the ':') shows either — (an emdash) or ◫. The emdash
means
there is no page associated with this item; the ◫ means there is a page. A
page
is an arbitrarily large body of text associated with the item. For example, an
item of 'took M3 and Noah to Sadies' is likely self-explanitory. However, if
something interesting happened there (you met a celebraty, someone accused you
falsely of harrassing them, etc.), you might want to add some explanatory
text.
Or if you have an idea that needs considerable information fleshed out for it,
you may have many pages worth of text associated with it.

The next field is a number called the item_id. This is a unique number that
identifies the item.

The next two items are dates. The first one is the date that the item was
created,
and the second one is the date the item was last updated. In this case, the
updated
date is None (NULL at the DB level).

Finally, the final portion of the log above is the item itself, in this case
'took M3 and Noah to Sadies'. This is divided from the metainformation by a
'|'.

Logging generally means setting out the various types in the journal in
unambigous,
concise and clear language. Logging involves making the words in the journal
entries
say as much as possible with as few words as possible. This is something
mastered over
time. You want the log, or idea, or quot or note to be as meaningful in 10
years as
it is now.

The following are other examples of logging:

```
jnl main.jnl --add --log 'work: info for Jenny'
LOG added...
jnl main.jnl --add --idea 'house project: colaborate with Joel'
IDEA added...
jnl main.jnl --add --quot 'To be, or not to be, that is the question.'
QUOT added...
jnl main.jnl --add --note 'work: info for Jenny in main project file'
NOTE added...

jnl main.jnl --ls
** TYPE ** : ** PAGE ** : ** ITEM_ID ** : ** CREATED ** : ** UPDATED ** : **
ITEM **

*** Logs, ideas, quotes, notes ***

• : — : 2: 2023-11-23 19:22:16: None | took M3 and Noah to Sadies
• : — : 3: 2023-11-23 19:35:20: None | work: info for Jenny
☼ : — : 4: 2023-11-23 19:35:57: None | house project: colaborate with Joel
” : — : 5: 2023-11-23 19:36:28: None | To be or not to be, that is the
question.
❃ : — : 6: 2023-11-24 16:37:05: None | work: info for Jenny in main project
file

*** Completed todos ***

*** No completed todo items ***

*** Open todos ***

*** No open todo items ***
```

This shows the possible logs you can use in the journal: a log (sorry for the
ambiguity in terminology) - •, an idea - ☼, a quot(e) - ” and a note - ❃.
These provide the core journal information, which is represented in the order
of the create date.

Although the item_id cannot and will not change, the create date can be
changed
with the following command:

```
jnl main.jnl --id 4 --dt "2023-11-20"
```

This will change the output of --ls to the following:

```
jnl main.jnl --ls
** TYPE ** : ** PAGE ** : ** ITEM_ID ** : ** CREATED ** : ** UPDATED ** : **
ITEM **

*** Logs, ideas, quotes, notes ***

☼ : — : 4: 2023-11-20 16:44:39: None | house project: colaborate with Joel
• : — : 2: 2023-11-23 19:22:16: None | took M3 and Noah to Sadies
• : — : 3: 2023-11-23 19:35:20: None | work: info for Jenny
” : — : 5: 2023-11-23 19:36:28: None | To be or not to be, that is the
question.
❃ : — : 6: 2023-11-24 16:37:05: None | work: info for Jenny in main project
file

*** Completed todos ***

*** No completed todo items ***

*** Open todos ***

*** No open todo items ***
```

Notice that item 4 is now at the top of the list, because the create date for
the item is earlier than the others in the journal.

Finally, you can add an arbitrary amount of data to each log. Consider the
following:

```
jnl main.jnl --add --log 'caught a nasty virus'
jnl main.jnl --id 7 --dt '2023-11-11'
```

Now I want to add the following to this log:

```
<snip>

################################################################################
I caught a nasty virus on 11/11/2023 and finally got to feeling better on
11/18/2023.

Aches, fever, chills for a solid week. I took IVM and HCQ to help get over it.

It didn't hit my lungs like Covid did.
<snip>
```

Simply edit a file, and put this information in it. I used temp.txt as a file
name. Then,

```
jnl main.jnl --id 7 --pg --file temp.txt
jnl main.jnl --id 7 --show_pg
• : ◫ : 7: 2023-11-11 20:12:03: 2023-12-15 21:10:06: caught nasty virus

################################################################################
I caught a nasty virus on 11/11/2023 and finally got to feeling better on
11/18/2023.

Aches, fever, chills for a solid week. I took IVM and HCQ to help get over it.

It didn't hit my lungs like Covid did.
```

There are other features you can use with your journal logs. Use

```
jnl main.jnl --help
```

to get a summary.

## Todos
Finally, I will cover todo logs. Todo logs are similar to other journal logs
except that they are designed to be top-level holders of todo information.
They might be a stand-alone todo item, like

```
jnl main.jnl --add --todo 'groceries: stock up at Sams'
TODO added...

dmay@dmay:~$ jnl main.jnl --ls
** TYPE ** : ** PAGE ** : ** ITEM_ID ** : ** CREATED ** : ** UPDATED ** : **
ITEM **

*** Logs, ideas, quotes, notes ***

• : ◫ : 7: 2023-11-11 17:02:54: 2023-11-24 17:05:44 | caught a nasty virus
☼ : — : 4: 2023-11-20 16:44:39: None | house project: colaborate with Joel
• : — : 2: 2023-11-23 19:22:16: None | took M3 and Noah to Sadies
• : — : 3: 2023-11-23 19:35:20: None | work: info for Jenny
” : — : 5: 2023-11-23 19:36:28: None | To be or not to be, that is the
question.
❃ : — : 6: 2023-11-24 16:37:05: None | work: info for Jenny in main project
file

*** Completed todos ***

*** No completed todo items ***

*** Open todos ***

✓ : — : 8: 2023-11-24 17:10:02: None | groceries: stock up at Sams
```

This is probably a one-time item, so once you have completed it, you can mark
it as --done.

```
jnl main.jnl --id 8 --done
Set item 8 to done...

jnl main.jnl --ls
<skipping...>
*** Completed todos ***

✗ : — : 8: 2023-11-24 17:10:02: 2023-11-24 17:11:23 | groceries: stock up at
Sams

*** Open todos ***

*** No open todo items ***
```

Then, it will be marked with an ✗ instead of a ✓. Notice that the logged
journal entries will simply scroll through at the top. They are logs,
basically. They show stuff that is important to track (log, if you will),
but is not stuff you are necessarily working on right now. The completed
todos and the open todos, however, are indicative of stuff you are working
on or have recently completed.

But todos are more powerful than this. Say, for example, that you want to
track todo items for a high-level todo.

```
jnl main.jnl --add --todo 'work: project with Jenny'
TODO added..
jnl main.jnl --ls
<skipping...>
*** Completed todos ***

✗ : — : 8: 2023-11-24 17:10:02: 2023-11-24 17:11:23 | groceries: stock up at
Sams

*** Open todos ***

✓ : — : 9: 2023-11-24 17:15:37: None | work: project with Jenny
```

So, we have a high-level project item. You can flesh this out with various
todo
items as follows:

```
cat temp.txt

################################################################################
[_] Lay out Scope of Work (SOW) for the project.
    [_] Work with stakeholders to clarify the idea.
    [_] Confirm budget, milestones and team members.
[_] Lay out project tasks and assign.
    [_] Define roles and objectives.
    [_] Communicate budget to team.
    [_] Schedule and implement scrum.
        [_] Initial few scrum meetings.
            [_] Assign tasks and duties, with clear deliverables and dates.
            [_] Cast the vision for the idea.
            [_] Set out initial timeline.
                [_] Verify with team the feasibility of maintaining the timeline.
                [_] Adjust deliverables accordingly.
            [_] Answer questions and set priorities.
    [_] Monitor project and set timelines moving forward.

```
Note: it is best practice to put the line of 80 hashes at the beginning of a
page of data.

```
jnl main.jnl --id 9--pg --file temp.txt
Added pg from temp.txt to item_id 9...

jnl main.jnl --id 9 --show_todo
✓ : ◫ : 9: 2023-11-24 17:15:37: 2023-11-24 17:24:34 | work: project with Jenny

################################################################################
[_] Lay out Scope of Work (SOW) for the project.
    [_] Work with stakeholders to clarify the idea.
    [_] Confirm budget, milestones and team members.
[_] Lay out project tasks and assign.
    [_] Define roles and objectives.
    [_] Communicate budget to team.
    [_] Schedule and implement scrum.
        [_] Initial few scrum meetings.
            [_] Assign tasks and duties, with clear deliverables and dates.
            [_] Cast the vision for the idea.
            [_] Set out initial timeline.
                [_] Verify with team the feasibility of maintaining the timeline.
                [_] Adjust deliverables accordingly.
            [_] Answer questions and set priorities.
    [_] Monitor project and set timelines moving forward.

Legend
===============
clear =>    [_]
done =>     [X]
delegate => [>]
cancel =>   [-]
now =>      [!]
soon =>     [+]
start =>    [/]
note =>     [*]
null =>     [?]
===============
```

Notice the legend. As you work through the project, you will add items, mark
them as done or not needed, prioritize them and move them around in the list
by priorities, enter clarifying notes and cancel them.

Editing this in an editor each time it changes may seem cumbersome, but I have
found through experience that this is the most fluid and flexible way to
manage a
body of tasks and track progress. For example, say you meet with the
stakeholders
and adjust the project tasks. First, edit the page associated with the project
and update it in the database:

```
jnl main.jnl --id 9 --pg --file temp.txt
Added pg from temp.txt to item_id 9...

jnl main.jnl --id 9 --show_todo
✓ : ◫ : 9: 2023-11-24 17:15:37: 2023-11-24 17:44:09 | work: project with Jenny

################################################################################
[X] Lay out Scope of Work (SOW) for the project.
    [X] Work with stakeholders to clarify the idea.
    [X] Confirm budget, milestones and team members.
        [*] Met with stakeholders 11/24. They confirmed our understanding of the main
            idea. They confirmed our budget of $85K (not including team member salaries).
            They liked our layout of milestones and gave us the thumbs up.

            The project is a go.
[_] Lay out project tasks and assign.
    [_] Define roles and objectives.
    [-] Communicate budget to team.
        [*] The team does not need this information.
    [_] Schedule and implement scrum.
        [_] Initial few scrum meetings.
            [_] Assign tasks and duties, with clear deliverables and dates.
            [_] Cast the vision for the idea.
            [_] Set out initial timeline.
                [_] Verify with team the feasibility of maintaining the timeline.
                [_] Adjust deliverables accordingly.
            [_] Answer questions and set priorities.
    [_] Monitor project and set timelines moving forward.

Legend
===============
clear =>    [_]
done =>     [X]
delegate => [>]
cancel =>   [-]
now =>      [!]
soon =>     [+]
start =>    [/]
note =>     [*]
null =>     [?]
===============
```

Once you have completed the project and handled all tasks as outlined, then
use --done on the project to end it.

```
jnl main.jnl --id 9 --show_todo
✓ : ◫ : 9: 2023-11-24 17:15:37: 2023-11-24 17:52:59 | work: project with Jenny

[X] Lay out Scope of Work (SOW) for the project.
    [X] Work with stakeholders to clarify the idea.
    [X] Confirm budget, milestones and team members.
        [*] Met with stakeholders 11/24. They confirmed our understanding of the main
            idea. They confirmed our budget of $85K (not including team member salaries).
            They liked our layout of milestones and gave us the thumbs up.

            The project is a go.
[X] Lay out project tasks and assign.
    [X] Define roles and objectives.
    [-] Communicate budget to team.
        [*] The team does not need this information.
    [X] Schedule and implement scrum.
        [X] Initial few scrum meetings.
            [>] Assign tasks and duties, with clear deliverables and dates.
                [*] You will want to note who is doing what.
            [X] Cast the vision for the idea.
            [X] Set out initial timeline.
                [-] Verify with team the feasibility of maintaining the timeline.
                [-] Adjust deliverables accordingly.
                    [*] Again, take copious notes and document.
            [X] Answer questions and set priorities.
    [X] Monitor project and set timelines moving forward.
    [*] Project completed 12/30/2023.

Legend
===============
clear =>    [_]
done =>     [X]
delegate => [>]
cancel =>   [-]
now =>      [!]
soon =>     [+]
start =>    [/]
note =>     [*]
null =>     [?]
===============

jnl main.jnl --id 9 --done
Set item 9 to done...
jnl main.jnl --ls
** TYPE ** : ** PAGE ** : ** ITEM_ID ** : ** CREATED ** : ** UPDATED ** : **
ITEM **
<skipping...>
*** Completed todos ***

✗ : — : 8: 2023-11-24 17:10:02: 2023-11-24 17:11:23 | groceries: stock up at
Sams
✗ : ◫ : 9: 2023-11-24 17:15:37: 2023-11-24 17:46:47 | work: project with Jenny

*** Open todos ***

*** No open todo items ***
```

I hope you enjoy using jnl as much as I do!

```
usage: jnl [-h] [-a] [--done] [--dt DT] [--edit] [--file FILE] [-i IDEA]
           [--id ID] [--item ITEM] [-l LOG] [--ls] [--all] [-n NOTE] [--pg]
           [-q QUOT] [--show_pg] [--show_todo] [--show_all_todos] [-t TODO]
           [--rm]
           FILENAME


positional arguments:
  FILENAME              The journal file name.

options:
  -h, --help            show this help message and exit
  -a, --add             Add a log or todo item
  --done                Flag a todo item given by id as done
  --dt DT               Change the create date for an item
  --edit                Edit a todo, log, note, idea or quot item
  --file FILE           Get a file name from the user
  -i IDEA, --idea IDEA  Add an idea item to the journal
  --id ID               Get an item id from the user
  --item ITEM           Get an item from the user for edit
  -l LOG, --log LOG     Add a log item to the journal
  --ls                  List all items
  --all                 List all items by date - works only with --ls
  -n NOTE, --note NOTE  Add a note item to the journal
  --pg                  Add a page to an item
  -q QUOT, --quot QUOT  Add a quote to the journal
  --show_pg             Print a page for an item
  --show_todo           Print the todo and its page on the screen for a given
                        todo item
  --show_all_todos      Print all todos/pages on the screen
  -t TODO, --todo TODO  Add a todo item to the journal
  --rm                  Move an item to the archive table


```