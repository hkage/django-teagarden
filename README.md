# Teagarden

Database modelling and planning software.

Teagarden is a webapplication used for database planning and
modelling during the software development process. With Teagarden software
developers and database architects can create database tables, fields,
constraints and relations without specifying the database system they want to
use for their project. Teagarden aims to be a database development platform and
documenation tool, but can also create the final SQL statements and compares the
specific, productive database against the modelling metadata schema.

## Why "teagarden"?

As this application is based upon the web framework Django and it was named
after "Django Reinhardt", a famous jazz musician, I thought of giving my project
also a name of a jazz legend. So I called it "teagarden", named after the famous
jazz trombonist [Jack Teagarden](http://de.wikipedia.org/wiki/Jack_Teagarden).

Teagarden is written in Python (django) and licensed under the MIT license.

## Features

Currently I am rebooting this project. Therefore the current feature list is not
freezed.

## Planned features

 * Backend for creating and managing projects, tables, fields etc.
 * Frontend to view projects, tables and fields
 * Composing table comments
 * RSS comment feed
 * Preview and create source files for tables in many dialects (e.g. PostgreSQL,
   Oracle, Python)
 * Visualization of tables and their references
 * Metadata / database comparison to create alter table statements

## Settings

* ``FIELD_POSITION_GAP`` (default: 10)
  Position gap between table fields.

.. |buildstatus| image:: https://travis-ci.org/hkage/teagarden.svg?branch=master
.. _buildstatus: http://travis-ci.org/hkage/django-teagarden
.. |coverage| image:: https://coveralls.io/repos/hkage/django-teagarden/badge.png?branch=master
.. _coverage: https://coveralls.io/repos/hkage/django-teagarden
