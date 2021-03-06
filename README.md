# Local Installation

  1. Navigate to the folder where you want to store this project.

  1. Run `git clone https://github.com/WolfElkan/hst3.git` to clone project to this folder. (Or download and unzip it.)

  1. Run `pip install virtualenv` to install the Virtual Environment software.

  1. Run `virtualenv -p python2 hst3env` to create a new Virtual Environment.

  1. Run `source hst3env/bin/activate` to activate Virtual Environment.

  1. Navigate into project folder (`cd hst3`)

  1. Run `sh HST/setup.sh` and follow the Terminal instructions

  1. Run `pip install -r requirements.txt` to install dependencies (This could take a few minutes).

  1. Run `python manage.py makemigrations` to create the data migration files.

  1. Start up a local MySQL server. (See [settings file](HST/settings.py#L94) for MySQL settings used in development.)

  1. Change the specs in settings file to point to your MySQL server if different configuration settings were used.

  1. Run `python manage.py migrate` to create the database on local server.

  1. Run `python manage.py runserver` to initialize application.

  1. Open web browser (Currently Google Chrome works best) and navigate to [localhost:8000](http://localhost:8000/). (Note: it's useful to have terminal window open and visible next to the browser for debugging purposes.)

  1. If application is running successfully, you will see an HST Homepage.  Click [JSON Bulk Data Interface](http://localhost:8000/seed/load/)

  1. Unzip the `hst.json.zip` file. (Note: this file contains confidential contact information for HST's families and, for privacy reasons, is **NOT** included in this repository or available anywhere on the web.  Contact the developer directly for this file.)

  1. Open `hst.json`, the file that unzips from `hst.json.zip`, in a Text Editor.  Copy the *entire text* of the file and paste it into the "JSON:" window on the application.

  1. Making sure you have the Terminal window visible (because it looks cool), click IMPORT.

  1. Once the data is successfully imported, navigate back to the [homepage](localhost:8000), and log in... somehow.

  1. Click [My Account](http://localhost:8000/myaccount/), [Admin Dashboard](http://localhost:8000/admin/dashboard/), [Create New Year's Courses](http://localhost:8000/admin/year/)

  1. Select the spring of the current year and click Continue

  1. Select all the HST Classes you want to run this year (including prepaid tickets) and click Create Courses

  1. Navigate back to the homepage.  The website is ready for use.

# Technical Documentation

  This website is built with [Django](https://www.djangoproject.com/), a Python-based, open-source web framework.  

## Objectives

  This web application is built with the following objectives in mind:

  1. To provide an intuitive, easy-to-use platform which users of varying computer skills can use to complete various functions necessary to the operation of HST,
  1. To allow HST to change, adapt and grow over the coming years, without requiring modification of the internal code of the application,
  1. To reduce the opportunity for human error, by automating any processes possible without causing undue complications,
  1. To reduce required volunteer time and allow HST to take full advantage of the digital age by streamlining data management processes wherever helpful,
  1. To be a blessing and an expression of God's love and providence to HST's staff, students and families as they have been to the developer.

## CSS

  Each HTML page loads the stylesheet `main/style.css`, this enables the style of all pages to be controlled from a single file.  (Some pages also load additional stylesheets for specific functions.)  

  Each page's `<body>` tag is given a (mostly) unique `id` by which it can be referenced, and its specific elements targeted.  Each page is also given a class: `public`, `admin`, `invoice`, `roster` or `error`.  (Some of the `admin` pages also have the class `rest`)  These tags divide the pages into groups based on who is supposed to see them.  This allows for separate styles for pages that HST families are supposed to see, vs pages for administrative use.

### Logo

  The HST [logo](https://www.hstonline.org/wp-content/uploads/2017/05/cropped-cropped-HST-LOGO-10.png) appears at the top of every page.  It has the CSS class `logo` and can be targeted, styled or hidden on certain pages.

### Close Button

  A Close button has been added to the bottom of every page which will close the window.  Note that this button *only works* if the window was opened with the JavaScript command `window.open("families.hstonline.org")`.  If the window was opened some other way, the button will act as a hyperlink and redirect the user to [`hstonline.org`](hstonline.org).  This button has the CSS class `close` and can be targeted, styled or hidden on certain pages.

## Apps

  This website contains 7 apps (located in the [apps](apps) folder) which handle different functionalities of the site.  They are alphabetically:

  **main** handles the static files and development views.

  **payment** handles invoices, tuition payments, and anything else having to do with money.

  **people** handles the students, families and faculty, as well as new family sign up.

  **program** handles the HST curriculum, including courses, enrollments and student eligibility.  (This app is unrelated to the printed program handed out at shows to audience members, and the name of the app may be changed [if desired](issues/17).)

  **radmin** handles administrative tasks such as invoice processing, audition results and course creation.  It would have been called `admin` but that clashes with the Django backend.  Besides we're rad enough, aren't we?

  **reports** handles the printable course rosters and any other printed reports.  New reports can be added [very quickly](issues/2)

  **rest** is a slightly buggy backend database interface.  This app handles the pages that tech support would be looking at when helping customers.  

### Low-Priority Apps

  These apps are not necessary for the May signup blitz, and theoretically could be built over the summer.  (However, I probably can also have them ready before the 2018 shows if needed:

  **shows** would handle scene conflicts, and anything else related only to the shows.

  **volunteer** would handle volunteer jobs, signup, hours, teams, captains, skills and anything else related to volunteers.

### Proposed Apps

  **vs**: Variety Show

  **sa**: Silent Auction

  **ths**: Honor Society

  **tickets**: Ticket sales (were we to decide to go that route)

### App Structure

#### Models

  Each `Model` class declaration defines attributes and methods in the following order:

  * Django database attributes
    * If not generated automatically, primary key is listed first
    * A static attribute which is a list of tuples used for `choices` in another attribute is defined immediately before that attribute.
    * `created_at`
    * `updated_at`
  * Other static attributes (e.g. `rest_model`)
  * Model Manager (`objects`)
  * Auto-call methods which take no arguments (other than `self`), which return:
    * A single value
    * A Django QuerySet
    * Something else
  * Methods which take multiple arguments whose primary goal is:
    * to return information
    * to make changes to the object itself
    * to make changes to other objects
  * Magic Methods
    * `__str__` first
    * `__getattribute__` last (institutes Auto-call)

An exception is made for methods whose primary purpose is to assist other methods. These are defined immediately after the methods they assist, regardless of the above order.

Methods which serve only to call methods on other objects should be used rarely.

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
    * `A`: Acting Classes
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
    * `X`: Tech Classes
    * `W`: Tech Workshops
    * `M`: Makeup
  * Non-Enrollable
    * `A`: Acting Scenes
    * `D`: Dance Classes (Combined)
    * `F`: Showcase Finale
    * `K`: Prepaid Tickets
    * `R`: Statistical
  * Other
    * Dummy courses for Development purposes (`EP`)
    * Historical courses (needed for Alumni Website)
    * Aliases (see [Antimony Protocol](#antimony-protocol))

  The letters `B`, `N`, `Q`, `U`, `V`, and `Y` are not currently in use.

#### Antimony Protocol

  HST produces 6 shows per year (7 including the Variety Show).  Each of these shows already has one or more 2-letter abbreviations: VS or SA for the Variety Show/Silent Auction, TT or CH for the Travel Troupe Coffee House (or AI for Acting Intensive), SC for Showcase, GB for Gaithersburg Troupe, SH for Shakespeare Troupe, JR for Junior Troupe, and SR for Senior Troupe.  Of these, 4 out of 7 have an abbreviation that starts with S (SA, SC, SH and SR).  It just so happens that these four shows are performed in alphabetical order of these abbreviations.  

  Furthermore, if the two younger troupes' ID's (GB and JR) were changed to an S followed by the first letter of the troupe name, they would become SG and SJ, which would *still* be alpha-chronological (SA, SC, SG, SH, SJ, SR).  The only exception is Travel Troupe which falls between the Silent Auction and Showcase.  The only option for this course that maintains the order is SB, which happens to be the symbol for the chemical element [Antimony](https://en.wikipedia.org/wiki/Antimony), which everyone knows is Travel Troupe's favorite periodic element!  Right?

  Anyway, by default, objects are always sorted by alphabetical order of their ID's, so having this order actually mean something is very helpful.  Also, for many internal functions, (particularly [Eligex](#eligex)) it is necessary to be able to distinguish different types of courses from their ID's alone, so having all troupe ID's begin with S is helpful here as well.

  The one disadvantage of the so-called "Antimony Protocol" is that it's confusing since we've been using JR and GB for so long.  This problem is solved with `CourseTrad` "aliasing".  In addition to the enrollable and non-enrollable courses, there are also 5 alias objects in the `CourseTrad` table.  These objects are called with the old non-Antimony abbreviation, but return the proper `CourseTrad` anyway.  **This means that you may use the Antimony or non-Antimony ID's, and you will still get the desired course.**  (This logic is performed at the `ModelManager` level, so it works in almost all contexts.)

#### Enrollable Courses

   ID  | Title| Ages    | Grades | Eligex| Notes
  :---:|-------------------------|:-------:|:------:|:-------------------------------:|:------------:
  `AA` | Acting A|  9 - 11 || `a`|  [1](#notes)
  `AB` | Acting B| 12 - 18 || `a`|  [1](#notes)
  `C1` | Broadway Choir| 10 - 18 || `a f`|  [2](#notes), [14](#notes)
  `C2` | A Cappella Choir| 14 - 18 || `a c @`|  [4](#notes), [14](#notes)
  `J1` | Jazz 1|  9 - 12 || `< a { ay @ } >`|  [5](#notes)
  `J2` | Jazz 2| 11 - 12 || `a < J2p { @ J1p } >`|  [6](#notes)
  `J3` | Jazz 3| 14 - 18 || `a < J3p { @ J2p } { @ Z2p } >` |  [7](#notes)
  `J4` | Jazz 4| 16 - 18 || `a < J4p { @ J3p } >`|  [6](#notes)
  `Z1` | Broadway Jazz 1| 13 - 18 || `a`|  [1](#notes), [15](#notes)
  `Z2` | Broadway Jazz 2| 13 - 18 || `a @`|  [3](#notes), [15](#notes)
  `T1` | Tap 1|  9 - 12 || `a`|  [1](#notes)
  `T2` | Tap 2| 11 - 12 || `a < T2p { @ T1p } >`|  [6](#notes)
  `T3` | Tap 3| 14 - 18 || `a < T3p { @ T2p } { @ P2p } >` |  [7](#notes)
  `T4` | Tap 4| 16 - 18 || `a < T4p { @ T3p } >`|  [6](#notes)
  `P1` | Broadway Tap 1| 13 - 18 || `a`|  [1](#notes), [15](#notes)
  `P2` | Broadway Tap 2| 13 - 18 || `a @`|  [3](#notes), [15](#notes)
  `IS` | Irish Dance Soft Shoe   |  9 - 18 || `a`|  [1](#notes)
  `IH` | Irish Dance Hard Shoe   | 11 - 18 || `a < I*p T*p P*p >`|  [8](#notes)
  `HB` | Boys Jazz &amp; Hip-Hop |  9 - 12 || `a m`|  [2](#notes)
  `HJ` | Jazz &amp; Hip-Hop| 13 - 18 || `a`|  [1](#notes)
  `SG` | Gaithersburg Troupe| 10 - 13 | 4 -  8 | `a g A*p S*p @`|  [9](#notes)
  `SJ` | Junior Troupe| 10 - 13 | 4 -  8 | `a g A*p S*p @`|  [9](#notes)
  `SB` | Travel Troupe| 14 - 18 || `a A*p`| [11](#notes)
  `SH` | Shakespeare Troupe| 14 - 18 | 9 - 12 | `a g A*p @`| [12](#notes)
  `SR` | Senior Troupe| 14 - 18 | 9 - 12 | `a g A*p @`| [12](#notes)
  `WN` | Painting Workshop| 14 - 18 || `a`|  [1](#notes)
  `WP` | Prop Workshop| 14 - 18 || `a`|  [1](#notes)
  `WW` | Wig Workshop| 14 - 18 || `a`|  [1](#notes)
  `WX` | Tech Crew Workshop| 12 - 18 || `a`|  [1](#notes)
  `XA` | Tech Apps| 12 - 18 || `a`|  [1](#notes)
  `XM` | Makeup Team| 14 - 18 || `a`|  [1](#notes)
  `XX` | Tech Team| 12 - 18 || `a WX`| [13](#notes)
  `GA` | JR/GB General Audition  | 10 - 13 | 4 -  8 | `a g A*p !S*p @`| [10](#notes)

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
  `#` | Always returns `True`. (Mostly used for classes with no prerequisites)
  `~` | Always returns `False`. (Mostly used for classes that are no longer offered)
  `a` | Returns whether the student meets the listed age requirement.
  `g` | Returns whether the student meets the listed grade requirement. (Always returns `True` if student does not have a `grad_year` listed.  Almost always returns `True` since most courses are for grades 1-12)
  `m` | Male: returns `True` for boys and `False` for girls
  `f` | Female: returns `True` for girls and `False` for boys
  `@` | Returns `True` if student has completed a successful audition or skill assessment for this class.  Returns `False` otherwise

#### Single-Letter Modifiers

  Glyph | Meaning
  :---: | ---
  `y` | Younger: may be appended to `a` or `g` to relax the *minimum* age or grade requirement by one year for each appended glyph (E. g., If a class is for ages 9-12, `ayy` will return True for 7-12 year olds and False otherwise)
  `o` | Older: just like `y` but relaxes the *maximum* age or grade requirement
  `e` | Limits query to only courses whose tradition's `e` variable is true, meaning the course will appear in Shopping Cart
  `u` | Limits query to only courses whose tradition's `m` variable is true, meaning the course will appear on Course Menu.  

#### Enrollment Search

  To require that a student have taken one HST class in order to be eligible for another, the two-letter `CourseTrad` ID of the prerequired course may be used as an Eligex word (E. g., `J2` will return True for students who are now, or have ever been, enrolled in a Jazz 2 class).  The glyph `*` may be substituted for either character in the ID, and will match any character.  E. g., `*4` will match any Level 4 class and `T*` will match any Tap class (Note: under the current system, `T*` will *not* match Broadway Tap classes, as these begin with `P`.  Likewise, `J*` will match Jazz classes, but not Broadway Jazz classes which are matched with `Z*`. See [note 15](#notes))

  To further refine these searches, the following modifiers may be appended *after* the class's ID:

  Glyph | Meaning
  :---: | ---
  `/` | Will match enrollments in previous years.  (If omitted, will match only current year)
  `$` | Will match only enrollments for which tuition has been paid
  `+` | Will match enrollments by anyone in student's family

  Note: Formerly, a tradition ID by itself would match enrollments in current *or* past years.  Since commit _______, this now only matches enrollments in the *current* year.  To match a course in current or past years, use [boolean operators](#boolean_operators)

  Desired Result | Old | New |
  --- | :---: | :---: |
  Match Jazz 2 this year | `J2c` | `J2` |
  Match Acting B in a previous year | `ABp` | `AB/` |
  Match Tech Workshop this year *or* previous years | `WX` | `< WX WX/ >` |
  Match any course this year | `c` | `**` |


  A student is considered eligible to audition for a course if they *would* be eligible to enroll in it, if they had passed an audition.

#### Boolean Operators

  Eligex is compiled conjunctively by default.  All words in an expression must be True for the expression to return True.  To modify this, use the following symbols:

  Glyph | Meaning
  :---: | ---
  `<` `>` | Words within trackets will be evaluated disjunctively, or OR'ed.  The compiler will first evaluate the expression within the trackets to see if *any* of them are true, and if so the entire tracketed expression will be treated as a single True value in the outer expression.  If all of the enclosed words evaluate as False, the tracketed expression will be evaluated as a single False value.
  `{` `}` | Braces are evaluated just like trackets, but words within them are AND'ed.  These are useful for nesting inside of trackets (AND within an OR within the default AND).  
  `!` | Not: May be appended before a word to return the opposite value.

  Note that enclosing symbols may not be nested within symbols of the same type.  `a < J2p { @ < J1p Z1p > } >` is an invalid expression because it contains trackets within trackets.  The expression `a < J2p { @ J1p } { @ Z1p } >` should be used instead, with the `@` distributed.

### Enrollments

The relationship between the `Student` table and the `Course` table is [many-to-many](https://en.wikipedia.org/wiki/Many-to-many_%28data_model%29) with an `Enrollment` table serving as the intermediate table.  Each `Enrollment` object contains `ForeignKey` links to the `Student` and `Course`, standard information about when the object was created and updated, as well as the `Enrollment`'s status.  The `status` field is an 8-character `CharField` that (currently) can have one of 24 values:

  Status   | Appearance | Note
---------- | :--------: | ----
`--------` | invisible | Default status, should not exist
`enrolled` | Green | Student is enrolled and paid
`eligible` | Bold on White | Student is currently eligible
`invoiced` | Orange | Enrollment is on an unpaid invoice
`need_pay` | Yellow | Enrollment has been added to cart
`not_elig` | Dark Gray | Student is not eligible
`aud_need` | Blue on White | Student is eligible for an Audition or Skill Assessment
`aud_pend` | Blue | Student has scheduled an Audition or Skill Assessment
`pendpass` | Blue | Deprecated: Teacher says student passed audition, but E.D. has not yet approved
`pendfail` | Blue | Deprecated: Teacher says student failed audition, but E.D. has not yet approved
`pend_pub` | Blue | Deprecated: Public-facing status for `pendpass` and `pendfail`
`fail_pub` | Dark Gray | Public-facing status for failed audition, no title text
`aud_pass` | Yellow | Student has passed Audition or Skill Assessment
`aud_fail` | Dark Gray | Student did not pass Audition or Skill Assessment
`aud_drop` | Bold on White | Student passed the Audition and then dropped course, but may re-enroll
`aud_lock` | Gold | Not in Use: Student has passed the Audition and *must* enroll
`conflict` | Red-Gray | Student is in another class at the same time
`need_cur` | Light Gray | Student will be eligible once they enroll in at least 1 other class
`needboth` | Light Gray | Student will be eligible to audition once they enroll in at least 1 other class
`nonexist` | invisible | Enrollment was added to invoice, and invoice was cancelled
`nopolicy` | Light Gray | Family has not yet accepted current HST Policy Agreement
`clasfull` | Dark Gray | The number of enrollments in this class meets or exceeds the class's capacity
`maydefer` | Yellow | Prepaid Tickets: This item may be deferred until Fall Parent Meeting
`deferred` | Purple | Prepaid Tickets: This item has been deferred until Fall Parent Meeting

## `radmin` app

### Invoice Check Acceptance

### Audition Results

### New Year

## `reports` app

### Master Enrollment Report

  Links to `rest` framework.

### Class Rosters

## `rest` app

A search bar has been added to the REST framework.  This search bar *is* case-sensitive.  A future commit will change this.

Also, if the search query contains the word "in", with a space on both sides, a search will be performed for Students matching the string to the left of "in" and another for Courses matching the string to the right of "in".  Finally, a list of enrollments for any of these students in any of these courses will be returned.

For example, searching for `Elkan in Troupe` will return any enrollments by students matching `Elkan` in courses matching `Troupe`.

## Development Features

### Hot Code

### Nuking

### Trace

## Utilities

