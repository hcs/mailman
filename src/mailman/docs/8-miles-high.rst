========================================
Notes from the PyCon 2012 Mailman Sprint
========================================

.. authorship
   The notes are based on Barry Warsaw's description of the Mailman 3
   pipeline at the PyCon 2012 Mailman sprint on March 13, with
   diagrams from his "Mailman" presentation at PyCon 2012.
   Transcribed by Stephen Turnbull.

*These are notes from the Mailman sprint at PyCon 2012.  They are not
terribly well organized, nor fully fleshed out.  Please edit and push
branches to Launchpad at lp:mailman or post patches to
<https://bugs.launchpad.net/mailman>.*

The intent of this document is to provide a view of Mailman 3's workflow and
structures from "eight miles high".


Basic Messaging Handling Workflow
=================================

Mailman accepts a message via the LMTP protocol (RFC 2033).  It implements a
simple LMTP server internally based on the LMTP server provided in the Python
standard library.  The LMTP server's responsibility is to parse the message
into a tuple (*mlist*, *msg*, *msgdata*).  If the parse fails (including
messages which Mailman considers to be invalid due to lack of `Message-Id` as
strongly recommended by RFC 2822 and RFC 5322), the message will be rejected,
otherwise the parsed message and metadata dictionary are pickled, and the
resulting *message pickle* added to one of the `in`, `command`, or `bounce`
processing queues.

.. graphviz::

   digraph msgflow {
     rankdir = LR;
     node [shape=box, color=lightblue, style=filled];
     msg [shape=ellipse, color=black, fillcolor=white];
     lmtpd [label="LMTP\nSERVER"];
     msg -> MTA [label="SMTP"];
     MTA -> lmtpd [label="LMTP"];
     lmtpd -> MTA [label="reject"];
     lmtpd -> IN -> PIPELINE [label=".pck"];
     lmtpd -> BOUNCES [label=".pck"];
     lmtpd -> COMMAND [label=".pck"];
   }

The `in` queue is processed by *filter chains* (explained below) to determine
whether the post (or administrative request) will be processed.  If not
allowed, the message pickle is discarded, rejected (returned to sender), or
held (saved for moderator approval -- not shown).  Otherwise the message is
added to the `pipeline` (i.e. posting) queue.

Each of the `command`, `bounce`, and `pipeline` queues is processed by a
*pipeline of handlers* as in Mailman 2's pipeline.  (Some functions such as
spam detection that were handled in the Mailman 2 pipeline are now in the
filter chains.)

Handlers may copy messages to other queues (*e.g.*, `archive`), and eventually
posted messages for distribution to the list membership end up in the `out`
queue for injection into the MTA.

The `virgin` queue is a special queue for messages created by Mailman.

.. graphviz::

   digraph pipeline {
   node [shape=box, style=rounded, group=0]
   { "MIME\ndelete" -> "cleanse headers" -> "add headers" -> \
     "calculate\nrecipients" -> "to digest" -> "to archive" -> \
     "to outgoing" }
   node [shape=box, color=lightblue, style=filled, group=1]
   { rank=same; PIPELINE -> "MIME\ndelete" }
   { rank=same; "to digest" -> DIGEST }
   { rank=same; "to archive" -> ARCHIVE }
   { rank=same; "to outgoing" -> OUT }
   }


Message Filtering
=================

Once a message has been classified as a post or administrivia, rules are
applied to determine whether the message should be distributed or acted on.
Rules include things like "if the message's sender is a non-member, hold it
for moderation", or "if the message contains an `Approved` header with a valid
password, allow it to be posted".  A rule may also make no decision, in which
case message processing is passed on to the next rule in the filter chain.
The default set of rules looks something like this:

.. graphviz::

   digraph chain_rules {
     rankdir=LR    /* This gives the right orientation of the columns. */
     rank=same
     subgraph in { IN [shape=box, color=lightblue, style=filled] }
     subgraph rules {
       rankdir=TB
       rank=same
       node [shape=record]
       approved [group=0, label="<f0> approved | {<f1> | <f2>}"]
       emergency [group=0, label="<f0> emergency | {<f1> | <f2>}"]
       loop [group=0, label="<f0> loop | {<f1> | <f2>}"]
       modmember [group=0, label="<f0> member\nmoderated | {<f1> | <f2>}"]
       administrivia [group=0, label="<f0> administrivia | <f1>"]
       maxsize [group=0, label="<f0> max\ size | {<f1> | <f2>}"]
       any [group=0, label="<f0> any | {<f1> | <f2>}"]
       truth [label="<f0> truth | <f1>"]
       approved:f1 -> emergency:f0 [weight=100]
       emergency:f1 -> loop:f0
       loop:f1 -> modmember:f0
       modmember:f1 -> administrivia:f0
       administrivia:f1 -> maxsize:f0
       maxsize:f1 -> any:f0
       any:f1 -> truth:f0
     }
     subgraph queues {
       rankdir=TB
       rank=same
       node [shape=box, style=filled];
       DISCARD [shape=invhouse, color=black, style=solid];
       MODERATION [color=wheat];
       HOLD [color=wheat];
     }
     { PIPELINE [shape=box, style=filled, color=cyan]; }

     IN -> approved:f0
     approved:f2 -> PIPELINE [minlen=2]
     loop:f2 -> DISCARD
     modmember:f2 -> MODERATION

     emergency:f2:e -> HOLD
     maxsize:f2 -> MODERATION
     any:f2 -> MODERATION
     truth:f1 -> PIPELINE [minlen=2]
   }


Configuration
=============

Uses lazr.config.

Each Runner's configuration object knows whether it should be started
when the Mailman daemon starts, and what queue the Runner manages.


Shell Commands
==============

`bin/mailman`: This is an ubercommand, with subcommands for all the various
things admins might want to do, similar to Mailman 2's mailmanctl, but with
more functionality.

`bin/master`: The runner manager: starts, watches, stops the runner
daemons.

`bin/runner`: Individual runner daemons.  Each instance is configured with
arguments specified on the command line.


User Model
==========

A *user* represents a person.  A user has an *id* and a *display
name*, and optionally a list of linked addresses.

Each *address* is a separate object, linked to no more than one user.

A list *member* associates an address with a mailing list.  Each list member
has a id, a mailing list name, an address (which may be `None`, representing
the user's *preferred address*), a list of preferences, and a *role* such as
"owner" or "moderator".  Roles are used to determine what kinds of mail the
user receives via that membership.  *Owners* will receive mail to
*list*-owner, but not posts and moderation traffic, for example.  A user with
multiple roles on a single list will therefore have multiple memberships in
that list, one for each role.

Roles are implemented by "magical, invisible" *rosters* which are objects
representing queries on the membership database.


List Styles
===========

Each list *style* is a named object.  Its attributes are functions used to
apply the relevant style settings to the mailing list *at creation time*.
Since these are functions, they can be composed in various ways, to create
substyles, *etc*.
