#!/usr/local/bin/python3.11
# -*- coding: utf-8 -*-
# vim: et:sts=4:sw=4

########################################################################################################################
### Start imports
########################################################################################################################
###
import sys
import os
import sqlite3 as sql
import argparse
import datetime
import time
###
########################################################################################################################
### End imports
########################################################################################################################

########################################################################################################################
### License - BSD 2-clause License
########################################################################################################################
###
### Copyright (c) 2023 David F May <david.f.may@gmail.com>
### 
### Redistribution and use in source and binary forms, with or without modification,
### are permitted provided that the following conditions are met:
### 
### * Redistributions of source code must retain the above copyright notice, this
###   list of conditions and the following disclaimer.
### 
### * Redistributions in binary form must reproduce the above copyright notice, this
###   list of conditions and the following disclaimer in the documentation and/or
###   other materials provided with the distribution.
### 
### THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
### ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
### WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
### DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
### ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
### (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
### LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
### ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
### (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
### SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
### 
########################################################################################################################

########################################################################################################################
# Broad outline
#
# Open jnl file provided on the command line
#     If it doesn't exist, create it
#     If it does exist, verify it
# Process config file - set defaults or use settings in config
# Parse command-line
# Process command-line
# If entry, enter log item or todo item
# If print, generate output with log entries in order first, and then todo items next
########################################################################################################################

########################################################################################################################
### External variables
########################################################################################################################
###
# Sqlite3 Connection objects.
con = None
cur = None
KEY_clear =   '❑'
KEY_bullet =  '•'
KEY_done =    '✗'
KEY_deleg =   '➤'
KEY_cancel =  '➘'
KEY_now =     '❗'
KEY_soon =    '➕'
KEY_start =   '➮'
KEY_note =    '❃'
KEY_null =    '❓'
KEY_emdash =  '—'
#KEY_idea =    '💡'
#KEY_idea =    '⛅'
KEY_idea =    '☼'
#KEY_quote =   '📒'
KEY_quote =   '”'
KEY_page =    '◫'
KEY_b_vs =    '✝'
KEY_check =   '✓'

dot = KEY_bullet
idea = KEY_idea
done = KEY_done
note = KEY_note
quot = KEY_quote
page = KEY_page
non = KEY_emdash
todo = KEY_check

legend = '''
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
'''

cmd = str
###
########################################################################################################################
### External variables
########################################################################################################################

########################################################################################################################
### Initialize DB file
########################################################################################################################
###
SQLInitialize = '''
BEGIN TRANSACTION;
-- =====================================================================================================================
-- items - primary table for the jnl application.
-- ---------------------------------------------------------------------------------------------------------------------
-- 
-- item_id - primary key for the item entry
-- item_type - type of the item
--    'NONE',             -- No type or type irrelevant
--    'TODO',             -- A todo item
--    'LOG',              -- Statement of a fact or information
--    'NOTE',             -- A notation
--    'IDEA',             -- An idea or possible project
--    'QUOT',             -- A quotation
--    'B_VS')),           -- Bible verse
-- dtime - timestamp when the record was created
-- updt - timestamp for the last update on the record
-- is_pg - True if there is a page associated with this item
-- is_pending - True if there is anything pending for the item
-- item - the text for the item
-- 
-- =====================================================================================================================

CREATE TABLE item (
  item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  item_type CHAR (4) CHECK (item_type IN ('NONE','TODO','LOG','NOTE','IDEA','QUOT','B_VS')),
  dtime TEXT,
  updt TEXT,
  is_pg BOOLEAN,
  is_done BOOLEAN,
  item TEXT
);
INSERT INTO item VALUES (NULL,'NONE',datetime('now','localtime'),NULL,NULL,NULL,'Journal item table created.');

-- =====================================================================================================================
--
-- page - additional information for the referenced item.
-- ---------------------------------------------------------------------------------------------------------------------
-- item-id - unique id of the item to which this page is associated
-- dtime - creation time of the page information
-- updt - time stamp of the most recent update
-- data - arbitrarily large field to hold the page information
--
-- =====================================================================================================================

CREATE TABLE page (
  item_id INTEGER,
  dtime TEXT,
  updt TEXT,
  data TEXT
);
INSERT INTO page VALUES (1,datetime('now','localtime'),NULL,'Journal page table created.');
CREATE INDEX page_id ON page(item_id);

-- =====================================================================================================================
-- cmd_line - track commands sent to the application
-- ---------------------------------------------------------------------------------------------------------------------
-- dtime - creation time of the record
-- cmd - actual command taken from the command-line
--     Note: This does not include the quotes which capture specific portions of the command as single
--     arguments. These commands should not be used as are on the command-line.
-- =====================================================================================================================

CREATE TABLE cmd_line (
    dtime TEXT,
    cmd TEXT
);
-- =====================================================================================================================
-- hours - tracks number of hours the todo item was worked on - not used now
-- ---------------------------------------------------------------------------------------------------------------------
-- item_id - unique value that represents the item
-- dtime - creation time of the page information
-- hours - hours, minutes the item was worked on
-- =====================================================================================================================

CREATE TABLE hours (
  item_id INTEGER,
  dtime TEXT,
  hours INTEGER,
  minutes INTEGER
);
INSERT INTO hours VALUES(1,datetime('now','localtime'),0,0);
CREATE INDEX hours_id ON hours(item_id);

-- =====================================================================================================================
-- journal - journal which tracks transactions on items
-- ---------------------------------------------------------------------------------------------------------------------
-- item_id - unique value that represents the item
-- dtime - creation time of the page information
-- hours - hours, minutes the item was worked on
-- =====================================================================================================================

-- CREATE TABLE journal (
--   item_id INTEGER,
--   type CHAR (2) CHECK (type IN ('INIT','ADD','PG','DONE','RM','ARCHIVE')),
--   dtime TEXT,
--   due TEXT,
--   todo TEXT,
--   data TEXT
-- );
-- INSERT INTO journal VALUES (1,'INIT',datetime('now','localtime'),NULL,'Journal journal table created.',NULL);

-- =====================================================================================================================
-- archive - table where deleted items are placed for archive
-- ---------------------------------------------------------------------------------------------------------------------
-- item_id - unique value that represents the item
-- dtime - creation time of the page information
-- updt - date of last update to the item record
-- archdt - time stamp item archived
-- item - text of actual items
-- data - page data stored
-- =====================================================================================================================

CREATE TABLE archive (
    item_id INTEGER,
    item_type CHAR (4) CHECK (item_type IN ('NONE','TODO','LOG','NOTE','IDEA','QUOT','B_VS')),
    dtime TEXT,
    updt TEXT,
    archdt TEXT,
    item TEXT,
    pg_data TEXT
);
INSERT INTO archive VALUES(1,NULL,datetime('now','localtime'),NULL,datetime('now','localtime'),'Journal archive table created.',NULL);
COMMIT;

-- =====================================================================================================================
'''
###
########################################################################################################################
### Initialize DB
########################################################################################################################

########################################################################################################################
### Main help
########################################################################################################################
################################################################################
main_help_description = '''
# jnl.py

## Getting started

jnl is a command-line application following the spirit of bullet journaling as
detailed in the Bullet Journal method by Ryder Carroll. It is written in Python,
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
to provide the jnl command with the name of the database file to initialize it.

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

After the above entry, you can get a listing of what is in the journal file with

```
jnl main.jnl --ls
 ** TYPE ** :  ** PAGE ** :  ** ITEM_ID ** :  ** CREATED ** :  ** UPDATED ** :  ** ITEM ** 

*** Logs, ideas, quotes, notes ***

• : — : 2: 2023-11-23 19:22:16: None | took M3 and Noah to Sadies

*** Completed todos ***

 *** No completed todo items *** 


*** Open todos ***

 *** No open todo items *** 
```

This looks a little intimidating, so let's step through it. The first line shows
you what the fields are in each entry. In this case, the log is given by a • as
the type. Other types are ideas (☼), notes (❃), quotes (”) and todos
(open todo = ✓, completed todo = ✗). We will talk about todos more later.

The next field (after the ':') shows either — (an emdash) or ◫. The emdash means
there is no page associated with this item; the ◫ means there is a page. A page
is an arbitrarily large body of text associated with the item. For example, an
item of 'took M3 and Noah to Sadies' is likely self-explanitory. However, if
something interesting happened there (you met a celebraty, someone accused you
falsely of harrassing them, etc.), you might want to add some explanatory text.
Or if you have an idea that needs considerable information fleshed out for it,
you may have many pages worth of text associated with it.

The next field is a number called the item_id. This is a unique number that
identifies the item.

The next two items are dates. The first one is the date that the item was created,
and the second one is the date the item was last updated. In this case, the updated
date is None (NULL at the DB level).

Finally, the final portion of the log above is the item itself, in this case
'took M3 and Noah to Sadies'. This is divided from the metainformation by a '|'.

Logging generally means setting out the various types in the journal in unambigous,
concise and clear language. Logging involves making the words in the journal entries
say as much as possible with as few words as possible. This is something mastered over
time. You want the log, or idea, or quot or note to be as meaningful in 10 years as
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
 ** TYPE ** :  ** PAGE ** :  ** ITEM_ID ** :  ** CREATED ** :  ** UPDATED ** :  ** ITEM ** 

*** Logs, ideas, quotes, notes ***

• : — : 2: 2023-11-23 19:22:16: None | took M3 and Noah to Sadies
• : — : 3: 2023-11-23 19:35:20: None | work: info for Jenny
☼ : — : 4: 2023-11-23 19:35:57: None | house project: colaborate with Joel
” : — : 5: 2023-11-23 19:36:28: None | To be or not to be, that is the question.
❃ : — : 6: 2023-11-24 16:37:05: None | work: info for Jenny in main project file

*** Completed todos ***

 *** No completed todo items *** 


*** Open todos ***

 *** No open todo items *** 
```

This shows the possible logs you can use in the journal: a log (sorry for the
ambiguity in terminology) - •, an idea - ☼,  a quot(e) - ” and a note - ❃.
These provide the core journal information, which is represented in the order
of the create date.

Although the item_id cannot and will not change, the create date can be changed
with the following command:

``` 
jnl main.jnl --id 4 --dt "2023-11-20"
```

This will change the output of --ls to the following:

```
 jnl main.jnl --ls
 ** TYPE ** :  ** PAGE ** :  ** ITEM_ID ** :  ** CREATED ** :  ** UPDATED ** :  ** ITEM ** 

*** Logs, ideas, quotes, notes ***

☼ : — : 4: 2023-11-20 16:44:39: None | house project: colaborate with Joel
• : — : 2: 2023-11-23 19:22:16: None | took M3 and Noah to Sadies
• : — : 3: 2023-11-23 19:35:20: None | work: info for Jenny
” : — : 5: 2023-11-23 19:36:28: None | To be or not to be, that is the question.
❃ : — : 6: 2023-11-24 16:37:05: None | work: info for Jenny in main project file

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

Finally, I will cover todo logs. Todo logs are similar to other journal logs
except that they are designed to be top-level holders of todo information. They
might be a stand-alone todo item, like

### CONTINUE HERE

jnl main.jnl --add --todo 'groceries: stock up at Sams'
TODO added...

dmay@dmay:~$ jnl main.jnl --ls
 ** TYPE ** :  ** PAGE ** :  ** ITEM_ID ** :  ** CREATED ** :  ** UPDATED ** :  ** ITEM ** 

*** Logs, ideas, quotes, notes ***

• : ◫ : 7: 2023-11-11 17:02:54: 2023-11-24 17:05:44 | caught a nasty virus
☼ : — : 4: 2023-11-20 16:44:39: None | house project: colaborate with Joel
• : — : 2: 2023-11-23 19:22:16: None | took M3 and Noah to Sadies
• : — : 3: 2023-11-23 19:35:20: None | work: info for Jenny
” : — : 5: 2023-11-23 19:36:28: None | To be or not to be, that is the question.
❃ : — : 6: 2023-11-24 16:37:05: None | work: info for Jenny in main project file

*** Completed todos ***

 *** No completed todo items *** 


*** Open todos ***

✓ : — : 8: 2023-11-24 17:10:02: None | groceries: stock up at Sams

This is probably a one-time item, so once you have completed it, you can mark it
as --done.

jnl main.jnl --id 8 --done
Set item 8 to done...

jnl main.jnl --ls
...
*** Completed todos ***

✗ : — : 8: 2023-11-24 17:10:02: 2023-11-24 17:11:23 | groceries: stock up at Sams

*** Open todos ***

 *** No open todo items *** 

Then, it will be marked with an ✗ instead of a ✓. Notice that the logged journal
entries will simply scroll through at the top. They are logs, basically. They
show stuff that is important to track (log, if you will), but is not stuff you
are necessarily working on right now. The completed todos and the open todos,
however, are indicative of stuff you are working on or have completed.

But todos are more powerful than this. Say, for example, that you want to track
todo items for a high-level todo.

jnl main.jnl --add --todo 'work: project with Jenny'
TODO added..
jnl main.jnl --ls
...
*** Completed todos ***

✗ : — : 8: 2023-11-24 17:10:02: 2023-11-24 17:11:23 | groceries: stock up at Sams

*** Open todos ***

✓ : — : 9: 2023-11-24 17:15:37: None | work: project with Jenny

So, we have a high-level project item. You can flesh this out with various todo
items as follows:

cat temp.txt

[_] Lay out Scope of Work (SOW) for the project.
    [_] Work with stakeholders to clarify the idea.
    [_] Define roles and objectives.
    [_] Schedule and implement scrum.
        [_] Initial few scrum meetings.
            [_] Assign tasks and duties, with clear deliverables and dates.
            [_] Cast the vision for the idea.
            [_] Set out initial timeline.
                [_] Verify with team the feasibility of maintaining the timeline.
                [_] Adjust deliverables accordingly.
            [_] Answer questions and set priorities.
    [_] Monitor project and set timelines.

jnl main.jnl --id 9--pg --file temp.txt
Added pg from temp.txt to item_id 9...

jnl main.jnl --id 9 --show_todo
✓ : ◫ : 9: 2023-11-24 17:15:37: 2023-11-24 17:24:34: work: project with Jenny

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

Notice the legend. As you work through the project, you will add items, mark
them as done or not needed, prioritize them and move them around in the list
by priorities, enter clarifying notes and cancel them.

I have found this by far to be the most fluid and flexible way to manage a
body of tasks and track progress. For example, say you meet with the stakeholders
and adjust the project tasks. First, edit the page associated with the project
and update it in the database:

jnl main.jnl --id 9 --pg --file temp.txt
Added pg from temp.txt to item_id 9...

jnl main.jnl --id 9 --show_todo
✓ : ◫ : 9: 2023-11-24 17:15:37: 2023-11-24 17:44:09: work: project with Jenny

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

Once you have completed the project and handled all tasks as outlined, then
use --done on the project to end it.

jnl main.jnl --id 9 --show_todo
✓ : ◫ : 9: 2023-11-24 17:15:37: 2023-11-24 17:52:59: work: project with Jenny

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
 ** TYPE ** :  ** PAGE ** :  ** ITEM_ID ** :  ** CREATED ** :  ** UPDATED ** :  ** ITEM ** 
...
*** Completed todos ***

✗ : — : 8: 2023-11-24 17:10:02: 2023-11-24 17:11:23 | groceries: stock up at Sams
✗ : ◫ : 9: 2023-11-24 17:15:37: 2023-11-24 17:46:47 | work: project with Jenny

*** Open todos ***

 *** No open todo items *** 

I hope you enjoy using jnl!
'''
################################################################################

is_ls = bool
is_pr = bool
is_add = bool
is_ls

########################################################################################################################
### Functions
########################################################################################################################
###

########################################################################################################################
### stamp_command
########################################################################################################################
def stamp_command (fn: str, cmd: str) -> bool:
    """Stamp the command-line into the cmd_line table."""
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False

    # Good sqlite file. Proceed.
    s = """BEGIN TRANSACTION; INSERT INTO cmd_line VALUES (datetime('now','localtime'),'{}'); COMMIT;""".format(cmd)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    # Done
    cur.close()
    con.close()
    return True

########################################################################################################################
### fixup_date
########################################################################################################################
def fixup_date (dt: str) -> str:
    """Append the date in dt with the current time. Must be YYYY-MM-DD format."""
    try:
        d = datetime.datetime.strptime(dt, '%Y-%m-%d')
    except ValueError:
        print ("*** Error: Date {} must be provided in 'YYYY-MM-DD' format".format (dt))
        sys.exit(3)
    cur = str
    cur = time.strftime ("%H:%M:%S", time.localtime())
    d = datetime.datetime.strptime(dt + ' ' + cur, '%Y-%m-%d %H:%M:%S')
    return str(d)

########################################################################################################################
### do_create_date
########################################################################################################################
def do_create_date (fn: str, id: str, dt: str) -> bool:
    """Change the create date of an item."""
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False

    # Good sqlite file. Proceed.
    s = """BEGIN TRANSACTION; UPDATE item SET dtime = '{}' WHERE item_id = {}; COMMIT;""".format(dt, id)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    # Done
    cur.close()
    con.close()
    return True

########################################################################################################################
### createJournalFile
########################################################################################################################
def createJournalFile (fn: str) -> bool:
    """Create a journal file given by filename 'fn'."""
    mycon = any
    mycur = any
    if os.path.isfile (fn):
        print ("Journal file {} already exists - nothing created.".format (fn))
        return True
    try:
        mycon = sql.connect (fn)
        mycur = mycon.cursor()
        mycur.executescript (SQLInitialize)
    except sql.Error as em:
        print ("*** SQLite error creating Journal file: {}".format (em))
        return False
    mycur.close()
    mycon.close()
    return True

########################################################################################################################
### do_log
########################################################################################################################
def do_log (fn: str, log: str) -> bool:
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    # Build the INSERT
    s = """BEGIN TRANSACTION; INSERT INTO item VALUES (NULL, 'LOG', datetime('now','localtime'), NULL, False, False,'{}'); COMMIT;""".format(log)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_note
########################################################################################################################
def do_note (fn: str, note: str) -> bool:
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    # Build the INSERT
    s = """BEGIN TRANSACTION; INSERT INTO item VALUES (NULL, 'NOTE', datetime('now','localtime'), NULL, False, False,'{}'); COMMIT;""".format(note)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_idea
########################################################################################################################
def do_idea (fn: str, idea: str) -> bool:
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    # Build the INSERT
    s = """BEGIN TRANSACTION; INSERT INTO item VALUES (NULL, 'IDEA', datetime('now','localtime'), NULL, False, False,'{}'); COMMIT;""".format(idea)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_quot
########################################################################################################################
def do_quot (fn: str, quot: str) -> bool:
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    # Build the INSERT
    s = """BEGIN TRANSACTION; INSERT INTO item VALUES (NULL, 'QUOT', datetime('now','localtime'), NULL, False, False,'{}'); COMMIT;""".format(quot)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_todo
########################################################################################################################
def do_todo (fn: str, td: str) -> bool:
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    # Build the INSERT
    s = """BEGIN TRANSACTION; INSERT INTO item VALUES (NULL, 'TODO', datetime('now','localtime'), NULL, False, False,'{}'); COMMIT;""".format(td)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_edit
########################################################################################################################
def do_edit (fn: str, id: str, itm: str) -> bool:
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    # Build the INSERT
    s = """BEGIN TRANSACTION; UPDATE item SET item = '{}',updt = datetime('now','localtime') WHERE item_id = {}; COMMIT;""".format(itm, id)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_ls
########################################################################################################################
def do_ls (fn: str) -> bool:
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    # Build the SELECT
    s = """SELECT * FROM item WHERE item_type IS NOT 'NONE' and item_type IS NOT 'TODO' ORDER BY dtime;"""
    try:
        cur.execute(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    ls_dat = []
    rows = cur.fetchall()
    # 0 = item_id, 1 = item_type, 2 = dtime, 3 = updt, 4 = is_pg, 5 = is_done, 6 = item
    s = '{}: {}: {}: {}: {}: {}'.format(' ** TYPE ** ', ' ** PAGE ** ',' ** ITEM_ID ** ', ' ** CREATED ** ', ' ** UPDATED ** ',' ** ITEM ** ')
    print (s)
    print ("\n*** Logs, ideas, quotes, notes ***\n")
    for r in rows:
        bullet = dot
        if r[1] == 'LOG':
            bullet = dot
        if r[1] == 'NOTE':
            bullet = note
        if r[1] == 'IDEA':
            bullet = idea
        if r[1] == 'QUOT':
            bullet = quot
        pg = str
        if r[4] == 0:
            pg = non
        else:
            pg = page
        s = '{} : {} : {}: {}: {} | {}'.format (bullet, pg, r[0], r[2], r[3], r[6])
        ls_dat.append (s)
    if len(ls_dat) == 0:
        print (" *** No items to output *** ")
    else:
        for s in ls_dat:
            print (s)
    # Next, grab completed todos and print them.
    s = """SELECT * FROM item WHERE item_type IS 'TODO' AND is_done IS 1 ORDER BY item_id"""
    try:
        cur.execute(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    ls_dat = []
    rows = cur.fetchall()
    # 0 = item_id, 1 = item_type, 2 = dtime, 3 = updt, 4 = is_pg, 5 = is_done, 6 = item
    print ("\n*** Completed todos ***\n")
    bullet = done
    for r in rows:
        pg = str
        if r[4] == 0:
            pg = non
        else:
            pg = page
        s = '{} : {} : {}: {}: {} | {}'.format (bullet, pg, r[0], r[2], r[3], r[6])
        ls_dat.append (s)
    if len(ls_dat) == 0:
        print (" *** No completed todo items *** \n")
    else:
        for s in ls_dat:
            print (s)
    # Next, grab current todos and print them.
    s = """SELECT * FROM item WHERE item_type IS 'TODO' and is_done IS 0 ORDER BY item_id;"""
    try:
        cur.execute(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    ls_dat = []
    rows = cur.fetchall()
    # 0 = item_id, 1 = item_type, 2 = dtime, 3 = updt, 4 = is_pg, 5 = is_done, 6 = item
    print ("\n*** Open todos ***\n")
    bullet = todo
    for r in rows:
        pg = str
        if r[4] == 0:
            pg = non
        else:
            pg = page
        s = '{} : {} : {}: {}: {} | {}'.format (bullet, pg, r[0], r[2], r[3], r[6])
        ls_dat.append (s)
    if len(ls_dat) == 0:
        print (" *** No open todo items *** \n")
    else:
        for s in ls_dat:
            print (s)
    # Done
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_rm
########################################################################################################################
def do_rm (fn: str, id: str) -> bool:
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    # Build the INSERT
    s = """SELECT item_type,dtime,updt,is_pg,item FROM item WHERE item_id = {}""".format(id)
    try:
        cur.execute(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    r = cur.fetchone()
    # 0 = item_id, 1 = item_type, 2 = dtime, 3 = updt, 4 = is_pg, 5 = is_done, 6 = item
    pg = str
    if not r:
        return False
    item_type = r[0]
    dtime = r[1]
    if dtime == None:
        dtime = 'NULL'
    updt = r[2]
    if updt == None:
        updt = 'NULL'
    is_pg = r[3]
    item = r[4]
    s = """BEGIN TRANSACTION; INSERT INTO archive VALUES({},'{}','{}','{}',datetime('now','localtime'),'{}','{}','NULL'); COMMIT;""".format (id,item_type,dtime,updt,is_pg,item)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    if is_pg:
        s = """SELECT data FROM page WHERE item_id IS {}""".format(id)
        try:
            cur.execute(s)
        except sql.Error as em:
            print ("*** Error: {} '{}'".format(s, em))
            cur.close()
            con.close()
            return False
        row = cur.fetchone()
        if row and row[0]:
            pg_data = row[0]
        pg_data = pg_data.replace("'","''")
        s = """BEGIN TRANSACTION; UPDATE archive SET pg_data = '{}' WHERE item_id = {}; COMMIT;""".format (pg_data,id)
        try:
            cur.executescript(s)
        except sql.Error as em:
            print ("*** Error: {} '{}'".format(s, em))
            cur.close()
            con.close()
            return False
    s = """BEGIN TRANSACTION; DELETE FROM item WHERE item_id = {}; COMMIT;""".format(id)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_pg
########################################################################################################################
def do_pg (fn: str, id: str, file: str) -> bool:
    """Associate a page of data to an item."""
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False

    # Good sqlite file. Proceed.

    # Open the file to add as a page
    f = open(file, "r")
    t = f.read()
    if ('\'' in str(t)):
        t = t.replace ("'","''")
    s = '''BEGIN TRANSACTION; DELETE FROM page WHERE item_id = {}'''.format (id)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    s = """BEGIN TRANSACTION; INSERT INTO page VALUES ({},datetime('now','localtime'),NULL, '{}'); COMMIT;""".format (id, t)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    s = """BEGIN TRANSACTION; UPDATE item SET updt = datetime('now','localtime'), is_pg = TRUE WHERE item_id = {}; COMMIT;""".format(id)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    # Done
    cur.close()
    con.close()
    return True

########################################################################################################################
### do_show_pg
########################################################################################################################
def do_show_pg (fn: str, id: str) -> bool:
    """Show the pg in fn given by id."""
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    s = """SELECT * FROM item WHERE item_id IS {} AND is_done is 0""".format(id)
    try:
        cur.execute(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    r = cur.fetchone()
    # 0 = item_id, 1 = item_type, 2 = dtime, 3 = updt, 4 = is_pg, 5 = is_done, 6 = item
    bullet = dot
    pg = str
    if not r:
        return False
    if r[1] == 'LOG':
        bullet = dot
    if r[1] == 'NOTE':
        bullet = note
    if r[1] == 'IDEA':
        bullet = idea
    if r[1] == 'QUOT':
        bullet = quot
    if r[4] and r[4] == 0:
        pg = non
    else:
        pg = page
    s = "{} : {} : {}: {}: {} | {}\n".format (bullet, pg, r[0], r[2], r[3], r[6])
    print (s)

    s = """SELECT data FROM page WHERE item_id IS {}""".format(id)
    try:
        cur.execute(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    row = cur.fetchall()
    for r in row:
        if r and r[0]:
            print (r[0])

    cur.close()
    con.close()
    return True

########################################################################################################################
### do_show_todo
########################################################################################################################
def do_show_todo (fn: str, id: str) -> bool:
    """Show the pg  for todo in fn given by id."""
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False
    # Good sqlite file. Proceed.

    s = """SELECT * FROM item WHERE item_type IS 'TODO' AND is_done IS 0 AND item_id IS {}""".format(id)
    try:
        cur.execute(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    r = cur.fetchone()
    # 0 = item_id, 1 = item_type, 2 = dtime, 3 = updt, 4 = is_pg, 5 = is_done, 6 = item
    bullet = todo
    pg = str
    if not r:
        return False
    if r[4] and r[4] == 0:
        pg = non
    else:
        pg = page
    s = "{} : {} : {}: {}: {} | {}".format (bullet, pg, r[0], r[2], r[3], r[6])
    print (s)

    s = """SELECT data FROM page WHERE item_id IS {}""".format(id)
    try:
        cur.execute(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False
    row = cur.fetchall()
    for r in row:
        if r and r[0]:
            print (r[0])
    print (legend)


    cur.close()
    con.close()
    return True
 

########################################################################################################################
### flag_todo_done
########################################################################################################################
def flag_todo_done (fn: str, id: str) -> bool:
    """Flag the todo item given by id in jnl file fn as done."""
    # Open journal file
    try:
        con = sql.connect (fn)
        cur = con.cursor()
    except sql.Error as em:
        print ("*** SQLite error opening Journal file: {}".format (em))
        return False

    # Verify it is a sqlite journal file.
    try:
        cur.execute('SELECT * FROM item WHERE item_type = "NONE"')
    except sql.Error as em:
        print ("***Error: {} '{}'".format(args.filename, em))
        cur.close()
        con.close()
        return False

    # Good sqlite file. Proceed.
    s = """BEGIN TRANSACTION; UPDATE item SET is_done = 1, updt = datetime('now','localtime') WHERE item_id = {}; COMMIT;""".format(id)
    try:
        cur.executescript(s)
    except sql.Error as em:
        print ("*** Error: {} '{}'".format(s, em))
        cur.close()
        con.close()
        return False

    cur.close()
    con.close()
    return True

###
########################################################################################################################
### Functions
########################################################################################################################

### Grab a quick snapshot of the command-line, pythonically
cmd = " ".join(sys.argv[:])

parser = argparse.ArgumentParser(
    prog="jnl",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=main_help_description)

parser.add_argument(
    'filename',
    type = str,
    help="The journal file name.",
    metavar="FILENAME")

parser.add_argument (
    '-a',
    '--add',
    action="store_true",
    dest="is_add",
    help = "Add a log or todo item")

# parser.add_argument (
#     '--cancel',
#     action="store_true",
#     dest="is_cancel",
#     help = "Flag a todo item given by id as cancelled")

# parser.add_argument (
#     '--delegate',
#     action="store_true",
#     dest="is_delegate",
#     help = "Flag a todo item given by id as delegated")

parser.add_argument (
    '--done',
    action="store_true",
    dest="is_done",
    help = "Flag a todo item given by id as done")

parser.add_argument (
    '--dt',
    dest='dt',
    help="Change the create date for an item",
    metavar="DT")

parser.add_argument (
    '--edit',
    action="store_true",
    dest="is_edit",
    help = "Edit a todo, log, note, idea or quot item")

parser.add_argument (
    '--file',
    dest='file',
    help="Get a file name from the user",
    metavar="FILE")

parser.add_argument (
    '-i',
    '--idea',
    dest='idea',
    help="Add an idea item to the journal",
    metavar="IDEA")

parser.add_argument (
    '--id',
    dest='id',
    help="Get an item id from the user",
    metavar="ID")

parser.add_argument (
    '--item',
    dest='item',
    help="Get an item from the user for edit",
    metavar="ITEM")

parser.add_argument (
    '-l',
    '--log',
    dest='log',
    help="Add a log item to the journal",
    metavar="LOG")

parser.add_argument (
    '--ls',
    action="store_true",
    dest="is_ls",
    help = "List all items")

parser.add_argument (
    '-n',
    '--note',
    dest='note',
    help="Add a note item to the journal",
    metavar="NOTE")

parser.add_argument (
    '--pg',
    action="store_true",
    dest="is_pg",
    help = "Add a page to an item")

parser.add_argument (
    '-q',
    '--quot',
    dest='quot',
    help="Add a quote to the journal",
    metavar="QUOT")

parser.add_argument (
    '--show_pg',
    action="store_true",
    dest="is_show_pg",
    help = "Print a page for an item")

parser.add_argument (
    '--show_todo',
    action="store_true",
    dest="is_show_todo",
    help="Print the todo and its page on the screen for a given todo item")

# parser.add_argument (
#     '--soon',
#     action="store_true",
#     dest="is_soon",
#     help = "Flag a todo item given by id as soon => high priority")

# parser.add_argument (
#     '--start',
#     action="store_true",
#     dest="is_start",
#     help = "Flag a todo item given by id as started")

parser.add_argument (
    '-t',
    '--todo',
    dest='todo',
    help="Add a todo item to the journal",
    metavar="TODO")

parser.add_argument (
    '--rm',
    action="store_true",
    dest='is_rm',
    help="Move an item to the archive table")

args = parser.parse_args()
cmd1 = None

if not args.filename:
    print ("***Error: The name of the journal file is required.")
    sys.exit(-1)
if not os.path.isfile(args.filename):
    # Create the file
    if not createJournalFile(args.filename):
        sys.exit(1)
    else:
        print ("Created journal file {}".format (args.filename))
        cmd1 = cmd

if args.is_add and args.log:
    cmd1 = '{} {} --add --log "{}"'.format (sys.argv[0], args.filename, args.log)
    ok = do_log(args.filename, args.log)
    if ok:
        print ("LOG added...")

if args.is_done:
    if not args.id:
        print ("*** Error: you must include --id <item_id> with a --done option.")
        sys.exit(3)
    cmd1 = '{} {} --id {} --done'.format(sys.argv[0], args.filename, args.id)
    ok = flag_todo_done(args.filename, args.id)
    if ok:
        print ("Set item {} to done...".format (args.id))

if args.dt:
    if not args.id:
        print ("*** Error: you must include --id <item_id> with a --dt option.")
        sys.exit(3)
    dt = fixup_date (args.dt)
    cmd1 = '{} {} --id {} --dt "{}"'.format (sys.argv[0],args.filename,args.id,args.dt)
    ok = do_create_date (args.filename, args.id, dt)

if args.is_edit:
    if not args.id:
        print ("*** Error: you must include --id <item_id> with an --edit option.")
        sys.exit(3)
    if not args.item:
        print ("*** Error: you must include --item <replacement item> with an --edit option.")
        sys.exit(3)
    cmd1 = '{} {} --id {} --item {} --edit'.format (sys.argv[0], args.filename, args.id, args.item)
    ok = do_edit (args.filename, args.id, args.item)
    if ok:
        print ("Edited item from item_id {} with '{}'...".format(args.id, args.item))

if args.todo and args.log:
    print ("*** Error: command-line: Can't provide todo and log on the same command")
    sys.exit(2)

if args.log and not args.is_add:
    print ("***Warning: You need --add with --log to add a log. Nothing changed.")

if args.is_add and args.note:
    cmd1 = '{} {} --add --note "{}"'.format (sys.argv[0], args.filename, args.note)
    ok = do_note(args.filename, args.note)
    if ok:
        print ("NOTE added...")

if args.note and not args.is_add:
    print ("***Warning: You need --add with --note to add a note. Nothing changed.")

if args.is_add and args.idea:
    cmd1 = '{} {} --add --idea "{}"'.format (sys.argv[0], args.filename, args.idea)
    ok = do_idea(args.filename, args.idea)
    if ok:
        print ("IDEA added...")

if args.idea and not args.is_add:
    print ("***Warning: You need --add with --idea to add an idea. Nothing changed.")

if args.is_add and args.quot:
    cmd1 = '{} {} --add --quot "{}"'.format (sys.argv[0], args.filename, args.quot)
    ok = do_quot(args.filename, args.quot)
    if ok:
        print ("QUOT added...")

if args.quot and not args.is_add:
    print ("***Warning: You need --add with --quot to add a quot. Nothing changed.")

if args.is_add and args.todo:
    # Enter a todo item
    cmd1 = '{} {} --add --todo "{}"'.format (sys.argv[0], args.filename, args.todo)
    ok = do_todo (args.filename, args.todo)
    if ok:
        print ("TODO added...")

if args.todo and not args.is_add:
    print ("***Warning: You need --add with --todo to add a todo item. Nothing changed.")

if args.is_pg:
    if not args.file:
        print ("*** Error: you must include --file <name> with a --pg option.")
        sys.exit(3)
    if not args.id:
        print ("*** Error: you must include --id <item_id> with a --pg option.")
        sys.exit(3)
    cmd1 = '{} {} --id {} --pg --file "{}"'.format (sys.argv[0], args.filename, args.id, args.file)
    ok = do_pg (args.filename, args.id, args.file)
    if ok:
        print ("Added pg from {} to item_id {}...".format(args.file, args.id))

if args.is_show_pg:
    if not args.id:
        print ("*** Error: you must include --id <item_id> with a --show_pg option.")
        sys.exit(3)
    cmd1 = '{} {} --id {} --show_pg'.format (sys.argv[0],args.filename,args.id)
    ok = do_show_pg (args.filename, args.id)

if args.is_show_todo:
    if not args.id:
        print ("*** Error: you must include --id <item_id> with a --show_todo option.")
        sys.exit(3)
    cmd1 = '{} {} --id {} --show_todo'.format (sys.argv[0], args.filename, args.id)
    ok = do_show_todo(args.filename, args.id)

if args.is_rm:
    if not args.id:
        print ("*** Error: you must include --id <item_id> with a --rm option.")
        sys.exit(3)
    cmd1 = '{} {} --id {} --rm'.format (sys.argv[0], args.filename, args.id)
    ok = do_rm(args.filename, args.id)

if args.is_ls or cmd1 is None:
    if args.is_add:
        print ("***Error: cannot add while doing an --ls")
        sys.exit(3)
    #cmd1 = '{} {} --ls'.format (sys.argv[0],args.filename)
    ok = do_ls(args.filename)
    if ok:
        sys.exit(0)
    else:
        sys.exit(1)

# Stamp the command into the cmd_line table.
ok = stamp_command (args.filename, cmd1)
if not ok:
    print ("*** Error: could not save command in cmd_line table")

