# Local Installation

  1. Clone or download to local system and navigate in Terminal to the directory where it's saved.

  1. Run `sudo apt-get install python-virtualenv` to install the Virtual Environment software.

  1. Run `mkvirtualenv hst3env` to create a new Virtual Environment.

  1. Run `source hst3env/bin/activate` to activate Virtual Environment.

  1. Run `python manage.py makemigrations` to create the data migration files.

  1. Start up a local MySQL server. (See [settings file](HST/settings.py#L94) for MySQL settings used in development.)

  1. Change the specs in settings file to point to your MySQL server if different configuration settings were used.

  1. Run `python manage.py migrate` to create the database on local server.

  1. Run `python manage.py runserver` to initialize application.

  1. Open web browser (Currently Google Chrome works best) and navigate to [localhost:8000](http://localhost:8000/). (Note: it's useful to have terminal window open and visible next to the browser for debugging purposes.)

  1. If application is running successfully, you will see an HST Homepage.  Click [JSON Bulk Data Interface](http://localhost:8000/seed/load/)

  1. Unzip the `hst.json.zip` file. (Note: this file contains confidential contact information for HST's families and, for privacy reasons, is NOT included in this repository or anywhere else on the web.  Contact the developer for this file.)

  1. Open `hst.json`, the file that unzips from `hst.json.zip`, in a Text Editor.  Copy the *entire text* of the file and paste it into the "JSON:" window on the application.

  1. Making sure you have the Terminal window visible (because it looks cool), click IMPORT.

  1. Once the data is successfully imported, navigate back to the homepage, and explore the website!

# Technical Documentation & User Guide

  This website is built with [Django](https://www.djangoproject.com/), a Python-based, open-source web framework.  

## Objectives

  This web application is built with the following objectives in mind:

  1. To provide an intuitive, easy-to-use platform which users of varying computer skills can use to complete various functions necessary to the operation of HST,
  1. To allow HST to change, adapt and grow over the coming years, without requiring modification of the internal code of the application,
  1. To reduce the opportunity for human error, by automating any processes possible without causing undue complications,
  1. To reduce required volunteer time and allow HST to take full advantage of the digital age by streamlining data management processes wherever helpful,
  1. To be a blessing and an expression of God's love and providence to HST's staff, students and families as they have been to the developer.

## Apps

  This website contains 7 apps (located in the [apps](apps) folder) which handle different functionalities of the site.  They are alphabetically:

  **main** handles the static files and development views.

  **payment** handles invoices, tuition payments, and anything else having to do with money.

  **people** handles the students, families and faculty, as well as new family sign up.

  **program** handles the HST curriculum, including courses, enrollments and student eligibility.  (This app is unrelated to the printed program handed out at shows to audience members, and the name of the app may be changed [if desired](#optional-features).)

  **radmin** handles administrative tasks such as invoice processing, audition results and course creation.  It would have been called `admin` but that clashes with the Django backend.  Besides we're rad enough, aren't we?

  **reports** handles the printable course rosters and any other printed reports.  New reports can be added [very quickly](#optional-features)

  **rest** is a slightly buggy backend database interface.  This app handles the pages that tech support would be looking at when helping customers.  

### Low-Priority Apps

  These apps are not necessary for the May signup blitz, and theoretically could be built over the summer.  (However, I probably can also have them ready before the 2018 shows [if needed](#optional-features))

  **shows** would handle scene conflicts, and anything else related only to the shows.

  **volunteer** would handle volunteer jobs, signup, hours, teams, captains, skills and anything else related to volunteers.

### Proposed Apps

  **vs**: Variety Show

  **sa**: Silent Auction

  **ths**: Honor Society

  **tickets**: Ticket sales (were we to decide to go that route)

### App Structure

#### Models

##### Migrations

#### Views

##### Templates

## `main` app

## `payment` app

## `people` app

## `program` app

### HST Class Traditions

  All HST classes are referred to as "courses" in the internal code of the site, to avoid clashing with the Python reserved word `class`.  Since HST generally runs the same courses every year, there are 2 types of course objects that the database uses.  There are the actual `Course` objects, which represent a given course in a given year (e.g. the 2013 Gaithersburg Troupe, or the 2018 Jazz 3 class) and there are course "tradition" or `CourseTrad` objects which represent the courses HST offers every year as timeless entities (e.g. Gaithersburg Troupe or Jazz 3).  There are 32 courses HST traditionally offers, plus 1 "General Audition."  They are listed [below](#enrollable-courses).

  In addition to these "enrollable" courses, Showcase Finale Groups, Acting Scenes, historical courses, prepaid tickets, and other entities may be represented as `CourseTrad` objects.  These non-enrollable courses are kept in the same table, and are distinguished from the enrollable courses using the boolean `e` attribute.  (See models)

  Each `CourseTrad` object has a 2-character ID, with the first letter indicating the genre or type of course, and the second indicating the course level or some other identifying characteristic.  The yearly `Course` objects have 4-character ID's: the last two digits of the year, followed by the 2-character `CourseTrad` ID.  The first letters of the `CourseTrad` ID's (and by extention, the 3rd character of the `Course` ID's) are as follows:

  * Classes in Showcase
    * `A`: Acting Classes ([note](#note-about-acting-classes))
    * `C`: Choirs
    * Dance Classes
      * Jazz
        * `J`: Jazz
        * `Z`: Broadway Jazz
      * Tap
        * `T`: Tap
        * `P`: Broadway Tap
      * `I`: Irish Dance
      * `H`: Jazz &amp; Hip Hop
  * `S`: Troupes ([note](#antimony-protocol))
  * Tech Program
    * `X`: Tech
    * `W`: Workshops
  * Non-Enrollable
    * `A`: Acting Scenes ([note](#note-about-acting-classes))
    * `F`: Showcase Finale
    * `G`: General Audition
    * `K`: Prepaid Tickets
  * Other
    * Historical courses (needed for Alumni Website)
    * Aliases (see [Antimony Protocol](#antimony-protocol))

  The letters `E`, `M`, `N`, `Q`, `R`, `U`, `V`, and `Y` are not currently in use.

#### Note About Acting Classes

  Ignoring aliases, `A` is the only letter that begins the ID's of both enrollable and non-enrollable courses.  `AA` and `AB` are [enrollable](#enrollable-courses).  `AC`, `A0`-`A9`, `AX`, `AY`, and `AZ` are [non-enrollable](#non-enrollable-courses).

#### Antimony Protocol

  HST produces 6 shows per year (7 including the Variety Show).  Each of these shows already has one or more 2-letter abbreviations: VS or SA for the Variety Show/Silent Auction, TT or CH for the Travel Troupe Coffee House (or AI for Acting Intensive), SC for Showcase, GB for Gaithersburg Troupe, SH for Shakespeare Troupe, JR for Junior Troupe, and SR for Senior Troupe.  Of these, 4 out of 7 have an abbreviation that starts with S (SA, SC, SH and SR).  It just so happens that these four shows are performed in alphabetical order of these abbreviations.  

  Furthermore, if the two younger troupes' ID's (GB and JR) were changed to an S followed by the first letter of the troupe name, they would become SG and SJ, which would *still* be alpha-chronological (SA, SC, SG, SH, SJ, SR).  The only exception is Travel Troupe which falls between the Silent Auction and Showcase.  The only option for this course that maintains the order is SB, which happens to be the symbol for the chemical element [Antimony](https://en.wikipedia.org/wiki/Antimony), which everyone knows is Travel Troupe's favorite periodic element!  Right?

  Anyway, by default, objects are always sorted by alphabetical order of their ID's, so having this order actually mean something is very helpful.

  The one disadvantage of the so-called "Antimony Protocol" is that it's confusing when we've been using JR and GB for so long.  This problem is solved with `CourseTrad` "aliasing".  In addition to the enrollable and non-enrollable courses, there are also 5 alias objects in the `CourseTrad` table.  These objects are called with the old non-Antimony abbreviation, but return the proper `CourseTrad` anyway.  This means that you may choose to use the Antimony or non-Antimony ID's, and you will still get the desired course.  (This logic is performed at the `ModelManager` level, so it works in almost all contexts.)

#### Enrollable Courses

   ID  | Title                   | Ages    | Grades | Eligex                          | Notes
  :---:|-------------------------|:-------:|:------:|:-------------------------------:|:------------:
  `AA` | Acting A                |  9 - 11 | 1 - 12 | `a`                             |  [1](#notes)
  `AB` | Acting B                | 12 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `C1` | Broadway Choir          | 10 - 18 | 1 - 12 | `a f`                           |  [2](#notes), [14](#notes)
  `C2` | A Cappella Choir        | 14 - 18 | 1 - 12 | `a c @`                         |  [4](#notes), [14](#notes)
  `J1` | Jazz 1                  |  9 - 12 | 1 - 12 | `< a { ay @ } >`                |  [5](#notes)
  `J2` | Jazz 2                  | 11 - 12 | 1 - 12 | `a < J2p { @ J1p } >`           |  [6](#notes)
  `J3` | Jazz 3                  | 14 - 18 | 1 - 12 | `a < J3p { @ J2p } { @ Z2p } >` |  [7](#notes)
  `J4` | Jazz 4                  | 16 - 18 | 1 - 12 | `a < J4p { @ J3p } >`           |  [6](#notes)
  `Z1` | Broadway Jazz 1         | 13 - 18 | 1 - 12 | `a`                             |  [1](#notes), [15](#notes)
  `Z2` | Broadway Jazz 2         | 13 - 18 | 1 - 12 | `a @`                           |  [3](#notes), [15](#notes)
  `T1` | Tap 1                   |  9 - 12 | 1 - 12 | `a`                             |  [1](#notes)
  `T2` | Tap 2                   | 11 - 12 | 1 - 12 | `a < T2p { @ T1p } >`           |  [6](#notes)
  `T3` | Tap 3                   | 14 - 18 | 1 - 12 | `a < T3p { @ T2p } { @ P2p } >` |  [7](#notes)
  `T4` | Tap 4                   | 16 - 18 | 1 - 12 | `a < T4p { @ T3p } >`           |  [6](#notes)
  `P1` | Broadway Tap 1          | 13 - 18 | 1 - 12 | `a`                             |  [1](#notes), [15](#notes)
  `P2` | Broadway Tap 2          | 13 - 18 | 1 - 12 | `a @`                           |  [3](#notes), [15](#notes)
  `IS` | Irish Dance Soft Shoe   |  9 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `IH` | Irish Dance Hard Shoe   | 11 - 18 | 1 - 12 | `a < I*p T*p P*p >`             |  [8](#notes)
  `HB` | Boys Jazz &amp; Hip-Hop |  9 - 12 | 1 - 12 | `a m`                           |  [2](#notes)
  `HJ` | Jazz &amp; Hip-Hop      | 13 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `SG` | Gaithersburg Troupe     | 10 - 13 | 4 -  8 | `a g A*p S*p @`                 |  [9](#notes)
  `SJ` | Junior Troupe           | 10 - 13 | 4 -  8 | `a g A*p S*p @`                 |  [9](#notes)
  `SB` | Travel Troupe           | 14 - 18 | 1 - 12 | `a A*p`                         | [11](#notes)
  `SH` | Shakespeare Troupe      | 14 - 18 | 9 - 12 | `a g A*p @`                     | [12](#notes)
  `SR` | Senior Troupe           | 14 - 18 | 9 - 12 | `a g A*p @`                     | [12](#notes)
  `WN` | Painting Workshop       | 14 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `WP` | Prop Workshop           | 14 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `WW` | Wig Workshop            | 14 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `WX` | Tech Crew Workshop      | 12 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `XA` | Tech Apps               | 12 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `XM` | Makeup Team             | 14 - 18 | 1 - 12 | `a`                             |  [1](#notes)
  `XX` | Tech Team               | 12 - 18 | 1 - 12 | `a WX`                          | [13](#notes)
  `GA` | JR/GB General Audition  | 10 - 13 | 4 -  8 | `a g A*p !S*p @`                | [10](#notes)

##### Notes:
  1. Students need only meet age requirements for Acting classes, Level 1 Tap, Broadway Tap or Broadway Jazz classes, Irish Soft Shoe, Co-ed Jazz &amp; Hip-Hop, Workshops, Tech Apps, or Makeup Team.
  2. Students must meet age requirements, and be a girl or boy to be in Broadway Choir or Boy's Jazz &amp; Hip-Hop respectively.
  3. Students must meet age requirements, and pass an audition or skill assessment for Level 2 Broadway Tap and Jazz classes.
  4. Students must meet age requirements, and be enrolled in at least 1 other class concurrently in order to audition for A Capella Choir.
  5. Students who meet age requirements may enroll in Jazz 1 immediately, but students who are 1 year too young may still audition.
  6. All students must meet age requirements.  Students who have already taken this class may enroll immediately.  Students who have taken the class 1 level below in the same genre may enroll if they pass an audition.
  7. Same as note 6, but previous enrollment in the preceding class's Broadway counterpart is also accepted.
  8. Students must meet age requirements, and have taken any Tap, Broadway Tap, or Irish class in the past.
  9. Students who meet age and grade requirements, have taken an acting class, and have already been in a troupe, may audition directly for Junior or Gaithersburg Troupe.
  10. Students who meet age and grade requirements, and have taken an acting class, but have *not* been a troupe, may audition jointly for both Junior and Gaithersburg Troupe.
  11. Students who meet age requirements, and have taken an Acting class, may enroll in Travel Troupe with no audition necessary.
  12. Students who meet age and grade requirements, and have taken an acting class, may audition for Senior or Shakespeare Troupes.
  13. Students who meet the age requirements and have taken the Tech Crew Workshop (either this year or in the past) may sign up for the Tech Team.
  14. The younger choir begins with B and the older choir begins with A, so to avoid the counterintuitive situation of having each choir's name begin with the letter from the code of the other choir, the numbers 1 and 2 are used instead.
  15. "Broadway" dance courses use the *last* letter of the genre, taP and jazZ.  Another option would be to use the first letter, but use A and B for levels 1 and 2 respectively.  There are pros and cons to both options which we can discuss.

#### Non-Enrollable Courses

<table>
  <thead><th>ID</th><th>Course</th><th>Note</th></thead>
  <tr><td><code>AC</code></td><td>Acting Combined</td><td>Used for Showcase conflict checking</td></tr>
  <tr><td><code>A0</code></td><td>Scene #0 (rarely used)</td><td rowspan="10">Showcase Acting Scenes</td></tr>
  <tr><td><code>A1</code></td><td>Scene #1</td></tr>
  <tr><td><code>A2</code></td><td>Scene #2</td></tr>
  <tr><td><code>A3</code></td><td>Scene #3</td></tr>
  <tr><td><code>A4</code></td><td>Scene #4</td></tr>
  <tr><td><code>A5</code></td><td>Scene #5</td></tr>
  <tr><td><code>A6</code></td><td>Scene #6</td></tr>
  <tr><td><code>A7</code></td><td>Scene #7</td></tr>
  <tr><td><code>A8</code></td><td>Scene #8</td></tr>
  <tr><td><code>A9</code></td><td>Scene #9 (rarely used)</td></tr>
  <tr><td><code>FN</code></td><td>Showcase Finale</td><td>All Showcase students in Finale</td></tr>
  <tr><td><code>F0</code></td><td>Showcase Finale Seniors</td><td rowspan="13">Individual Finale groups</td></tr>
  <tr><td><code>F1</code></td><td>Showcase Finale Group #1</td></tr>
  <tr><td><code>F2</code></td><td>Showcase Finale Group #2</td></tr>
  <tr><td><code>F3</code></td><td>Showcase Finale Group #3</td></tr>
  <tr><td><code>F4</code></td><td>Showcase Finale Group #4</td></tr>
  <tr><td><code>F5</code></td><td>Showcase Finale Group #5</td></tr>
  <tr><td><code>F6</code></td><td>Showcase Finale Group #6</td></tr>
  <tr><td><code>F7</code></td><td>Showcase Finale Group #7</td></tr>
  <tr><td><code>F8</code></td><td>Showcase Finale Group #8</td></tr>
  <tr><td><code>F9</code></td><td>Showcase Finale Group #9</td></tr>
  <tr><td><code>FX</code></td><td>Showcase Finale Group #10 (Roman Numeral X)</td></tr>
  <tr><td><code>FY</code></td><td>Showcase Finale Group #11</td></tr>
  <tr><td><code>FZ</code></td><td>Showcase Finale Group #12</td></tr>
  <tr><td><code>KB</code></td><td>10 Prepaid Tickets to Coffee House</td><td rowspan="6">Prepaid Tickets</td></tr>
  <tr><td><code>KC</code></td><td>10 Prepaid Tickets to Showcase</td></tr>
  <tr><td><code>KG</code></td><td>10 Prepaid Tickets to Gaithersburg Troupe</td></tr>
  <tr><td><code>KH</code></td><td>10 Prepaid Tickets to Shakespeare Troupe</td></tr>
  <tr><td><code>KJ</code></td><td>10 Prepaid Tickets to Junior Troupe</td></tr>
  <tr><td><code>KR</code></td><td>10 Prepaid Tickets to Senior Troupe</td></tr>
  <tr><td><code>BT</code></td><td>Ballet</td><td rowspan="5">Historical</td></tr>
  <tr><td><code>DI</code></td><td>Dance Intensive</td></tr>
  <tr><td><code>LN</code></td><td>Interpretive Sign Language</td></tr>
  <tr><td><code>O1</code></td><td>Overture 1</td></tr>
  <tr><td><code>O2</code></td><td>Overture 2</td></tr>
  <tr><td><code>GB</code></td><td><code>GB</code> &rarr; <code>SG</code> (Gaithersburg Troupe)</td><td rowspan="5">Aliases</td></tr>
  <tr><td><code>JR</code></td><td><code>JR</code> &rarr; <code>SJ</code> (Junior Troupe)</td></tr>
  <tr><td><code>TT</code></td><td><code>TT</code> &rarr; <code>SB</code> (Travel Troupe)</td></tr>
  <tr><td><code>CH</code></td><td><code>CH</code> &rarr; <code>SB</code> (Coffee House)</td></tr>
  <tr><td><code>AI</code></td><td><code>AI</code> &rarr; <code>SB</code> (Acting Intensive)</td></tr>
  </table>

### Eligex

  This web application can automatically determine whether a given student is eligible for a given course in a given year.  However, due to the complicated nature of the eligibility requirements for many of HST's classes, it was necessary to develop an expression language to determine eligibility of students.  "Eligibility Expressions" (or Eligex) is a language in which any requirements and prerequisites for an HST class can be written and will be understood by the server.  It also enables requirements to be written for future classes HST may offer, or to modify the requirements for existing classes, without rewriting the internal code of the website.  It may look daunting, but it's really just boolean algebra (True and False statements).

  A line of Eligex is case-sensitive and contains one or more "words" (separated by spaces) which are converted into True or False values.  Unless trackets (`<` `>`) are used, these values will be compiled conjunctively, or AND'ed.  That is to say, if any of the words is False, the expression will return False, and the student will not be eligible for the class.  Only if all the words are True, will the expression return True and the student will be eligible for the class.

#### Single-Letter Words

  Note: Letters with special meanings are lowercase to avoid clashing with ID's of specific courses, represented by CAPITAL letters.

  Glyph | Meaning |
  :---: | --- |
  `#` | Always returns True. (Mostly used for classes with no prerequisites)
  `~` | Always returns False. (Mostly used for classes that are no longer offered)
  `a` | Returns whether the student meets the listed age requirement.
  `g` | Returns whether the student meets the listed grade requirement. (Always returns true if student does not have a `grad_year` listed.  Almost always returns true since most courses are for grades 1-12)
  `m` | Male: returns true for boys and false for girls
  `f` | Female: returns true for girls and false for boys
  `@` | Searches for a *successful* audition or skill assessment for the class by the student.  (If no `@` is included, word will match only actual enrollments, not auditions.)
  `%` | Returns the value of the global variable `DEV`.  (True in development &amp; testing, False in production.)

#### Single-Letter Modifiers

  Glyph | Meaning
  :---: | ---
  `y` | Younger: may be appended to `a` or `g` to relax the *minimum* age or grade requirement by one year for each appended glyph (E. g., If a class is for ages 9-12, `ayy` will return True for 7-12 year olds and False otherwise)
  `o` | Older: just like `y` but relaxes the *maximum* age or grade requirement

#### Enrollment Search

  To require that a student have taken one HST class in order to be eligible for another, the two-letter `CourseTrad` ID of the prerequired course may be used as an Eligex word (E. g., `J2` will return True for students who are now, or have ever been, enrolled in Jazz 2).  The glyph `*` may be substituted for either character in the ID, and will match any character.  E. g., `*4` will match any Level 4 class and `T*` will match any Tap class (Note: under the current system, `T*` will *not* match Broadway Tap classes, as these begin with `P`.  Likewise, `J*` will match Jazz classes, but not Broadway Jazz classes which are matched with `Z*`. See [note 15](#notes))

  To further refine these searches, the following modifiers may be appended *after* the class's ID:

  Glyph | Meaning
  :---: | ---
  `c` | Will match only enrollments in the *current* year
  `p` | Will match only enrollments in *past* or *previous* years.
  `$` | Will match only enrollments for which tuition has been paid
  `+` | Will match enrollments by anyone in student's family

  Note: A student is considered eligible to audition for a course if they *would* be eligible to enroll in it, if they had passed an audition.

  Note: Presents go under Christmas Trees, not in Eligexes.  If you put a `p` after an eligex word in the hopes of matching "present" enrollments, you will be disappointed.

#### Boolean Operators

  Eligex is compiled conjunctively by default.  All words in an expression must be True for the expression to return True.  To modify this, use the following symbols:

  Glyph | Meaning
  :---: | ---
  `<` `>` | Words within trackets will be evaluated disjunctively, or OR'ed.  The compiler will first evaluate the expression within the trackets to see if *any* of them are true, and if so the entire tracketed expression will be treated as a single True value in the outer expression.  If all of the enclosed words evaluate as False, the tracketed expression will be evaluated as a single False value.
  `{` `}` | Braces are evaluated just like trackets, but words within them are AND'ed.  These are useful for nesting inside of trackets (AND within an OR within the default AND).  
  `!` | Not: May be appended before a word to return the opposite value.

  Note that enclosing symbols may not be nested within symbols of the same type.  `a < J2p { @ < J1p Z1p > } >` is an invalid expression because it contains trackets within trackets.  The expression `a < J2p { @ J1p } { @ Z1p } >` should be used instead, with the `@` distributed.

## `radmin` app

## `reports` app

## `rest` app

## Development Features

### Hot Code

### Nuking

### Trace

## Utilities

# Optional Features
  
  * More reports
  * Student Special Needs field
  * Cancel Courses
  * Do you want to be able to schedule when enrollment for a course opens?
  * Partial Invoice Payment
  * Secure sessions (Django or scratch?)
  * Trade security for convenience: Confirm rather than require invoice code
  * Timeless Master Enrollment Report
  * Human-readable eligex translator
  * Hover over course to see why student is not eligible
  * Tests

# Other Questions

  * Beta testing?
  * What did we decide about login by email?
  * GB/JR General Audition (Audition results interface)
