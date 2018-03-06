# Local Installation

After setting up the application with Django, open the file `coursetrads.json`, and copy the text of the file.  Go to `/seed/load/`, paste the text into the JSON window and click import.  

# HST Website Django Backend
*Technical Documentation & User Guide*

## Objectives

This web application is built with the following objectives in mind:

1. To provide an intuitive, easy-to-use platform which users of varying computer skills can use to complete various functions necessary to the operation of HST,
1. To allow HST to change, adapt and grow over the coming years, without requiring modification of the internal code of the application,
1. To reduce the opportunity for human error, by automating any processes possible without causing undue complications,
1. To reduce required volunteer time and allow HST to take full advantage of the digital age by streamlining data management processes wherever helpful,
1. To be a blessing and an expression of God's love and providence to HST's staff, students and families as they have been to the developer.

## Eligex

This web application can determine whether a given student is eligible for a given course in a given year.  However, due to the complicated nature of the eligibility requirements for many of HST's classes, it was necessary to develop an expression language to determine eligibility of students.  Eligex is a language that in which any requirements and prerequisites for an HST class can be written and will be understood by the server.  It also enables requirements to be written for future classes HST may offer, or to modify the requirements for existing classes, without rewriting the internal code of the website.  It may look daunting, but it's really just boolean algebra (True and False statements).

A line of Eligex is case-sensitive and contains one or more "words", separated by spaces which are converted into True or False values.  Unless trackets (`<` `>`) are used, these values will be compiled conjunctively, or AND'ed.  That is to say, if any of the words is False, the expression will return False, and the student will not be eligible for the class.  Only if all the words are True, will the expression return True and the student will be eligible for the class.

### Single-Letter Words
Note: Letters with special meanings are lowercase to avoid clashing with capital letters which refer to `CourseTrad` id's.
Glyph | Meaning
:---: | ---
`#` | Always returns True
`~` | Always returns False
`a` | Returns whether the student meets the age requirements
`g` | Returns whether the student meets the grade requirements (Always returns true if student does not have a `grad_year` listed.  Almost always returns true since most courses are for grades 1-12)
`m` | Male: returns true for boys and false for girls
`f` | Female: returns true for girls and false for boys
`@` | Searches for a *successful* audition or skill assessment for the class by the student.  (If no `@` is included, word will match only actual enrollments, not auditions.)
`%` | Returns the value of the global variable `DEV`.  (True in development &amp; testing, False in production.)
### Single-Letter Modifiers
Glyph | Meaning
:---: | ---
`y` | Younger: may be appended to `a` or `g` to relax the *minimum* age or grade requirement by one year for each appended glyph (E. g., If a class is for ages 9-12, `ayy` will return True for 7-12 year olds and False otherwise)
`o` | Older: just like `y` but relaxes the *maximum* age or grade requirement
### Enrollment Search
To require that a student have taken another HST class in order to be eligible for this one, the two-letter ID of the class may be used as an Eligex word (E. g., `J2` will return True for students who are now, or have ever been, enrolled in Jazz 2).  The glyph `*` may be substituted for either character in the ID, and will match any character.  E. g., `*4` will match any Level 4 class and `T*` will match any Tap class (Note: under the current system, `T*` will *not* match Broadway Tap classes, as these begin with `P`.  Likewise, `J*` will match Jazz classes, but not Broadway Jazz classes which are matched with `Z*`)
To further refine these searches, the following modifiers may be appended *after* the class's ID:

Glyph | Meaning
:---: | ---
`c` | Will match only enrollments in the *current* year
`p` | Will match only enrollments in *past* years.
`$` | Will match only enrollments for which tuition has been paid
`+` | Will match student's whole family
Note: A student is considered eligible to audition for a course if they would be eligible to enroll in it, should they pass an audition.

### Boolean Operators

Eligex is compiled conjunctively by default.  All words in an expression must be True for the expression to return True.  To modify this, use the following symbols:

Glyph | Meaning
:---: | ---
`<` `>` | Words within trackets will be evaluated disjunctively, or OR'ed.  The compiler will first evaluate the expression within the trackets to see if *any* of them are true, and if so the entire tracketed expression will be treated as a single True value in the outer expression.  If all of the enclosed words evaluate as False, the tracketed expression will be evaluated as a single False value.
`{` `}` | Braces are evaluated just like trackets, but words within them are AND'ed.  These are useful for nesting inside of trackets (AND within an OR within an AND).  Note that enclosing symbols may not be nested within symbols of the same type.  `< a { T3p @ < P2p T2p > } >` is an invalid expression because it contains trackets within trackets.
`!` | Not: May be appended before a word to return the opposite value

### Examples

Eligex | Class | Description
:------: | :---: | ------------
`a g` | All classes not listed here | Student must meet age and grade requirements.  
`a g f`<br>`a g m`|Broadway Choir<br>Boys Jazz &amp; Hip Hop| Student must meet age and grade requirements, <br>and be a girl or boy respectively.
`a g @ **c`|A Capella Choir| Students must meet age and grade requirements, <br>pass an audition, and be currently enrolled in at <br>least 1 other class.
`< a { ay @ } >`|Jazz 1| Students who meet the age requirement <br>may enroll immediately, but students who <br>are 1 year too young may audition.
`a g @`|Broadway Tap 2<br>Broadway Jazz 2|Students must meet age and grade requirements<br>and pass a skill assessment.
`a g < T2p { @ T1p } >`<br>`a g < T4p { @ T3p } >`<br>`a g < J2p { @ J1p } >`<br>`a g < J4p { @ J3p } >`|Tap 2<br>Tap 4<br>Jazz 2<br>Jazz 4<br>|In addition to age and grade, students<br>either have taken the class one level <br>below this and pass a skill assessment, <br>or have already taken this class.
`a g < T3p { @ T2p } { @ P2p } >`||
`a g < I*p T*p P*p >` || Students must meet age and grade requirements <br>and have formerly taken either an Irish class, or a <br>Tap or Broadway Tap class. 
`a g A*p @`           ||  Students must meet age and grade requirements, <br>and have taken an Acting class in order to audition 

<!-- ## Antimony Protocol -->

## HST Class Traditions

All HST classes are referred to as "courses" in the internal code of the site, to avoid clashing with the Python reserved word `class`.  `CourseTrad`

### Enrollable Classes
 ID  | Title                   | Ages    | Grades | Eligex                           | Note
:---:|-------------------------|:-------:|:------:|:--------------------------------:|-----:
`AA` | Acting A                |  9 - 11 | 1 - 12 | `a`                              | 1
`AB` | Acting B                | 12 - 18 | 1 - 12 | `a`                              | 1
`C1` | Broadway Choir          | 10 - 18 | 1 - 12 | `a f`                            | 2
`C2` | A Cappella Choir        | 14 - 18 | 1 - 12 | `a c @@`                         | 4
`J1` | Jazz 1                  |  9 - 12 | 1 - 12 | `< a { ay @@ } >`                | 5
`J2` | Jazz 2                  | 11 - 12 | 1 - 12 | `a < J2p { @@ J1p } >`           | 6
`J3` | Jazz 3                  | 14 - 18 | 1 - 12 | `a < J3p { @@ J2p } { @@ Z2p } >`| 7
`J4` | Jazz 4                  | 16 - 18 | 1 - 12 | `a < J4p { @@ J3p } >`           | 6
`Z1` | Broadway Jazz 1         | 13 - 18 | 1 - 12 | `a`                              | 1
`Z2` | Broadway Jazz 2         | 13 - 18 | 1 - 12 | `a @@`                           | 3
`T1` | Tap 1                   |  9 - 12 | 1 - 12 | `a`                              | 1
`T2` | Tap 2                   | 11 - 12 | 1 - 12 | `a < T2p { @@ T1p } >`           | 6
`T3` | Tap 3                   | 14 - 18 | 1 - 12 | `a < T3p { @@ T2p } { @@ P2p } >`| 7
`T4` | Tap 4                   | 16 - 18 | 1 - 12 | `a < T4p { @@ T3p } >`           | 6
`P1` | Broadway Tap 1          | 13 - 18 | 1 - 12 | `a`                              | 1
`P2` | Broadway Tap 2          | 13 - 18 | 1 - 12 | `a @@`                           | 3
`IS` | Irish Dance Soft Shoe   |  9 - 18 | 1 - 12 | `a`                              | 1
`IH` | Irish Dance Hard Shoe   | 11 - 18 | 1 - 12 | `a < I*p T*p P*p >`              | 8
`HB` | Boys Jazz &amp; Hip-Hop |  9 - 12 | 1 - 12 | `a m`                            | 2
`HJ` | Jazz &amp; Hip-Hop      | 13 - 18 | 1 - 12 | `a`                              | 1
`GA` | JR/GB General Audition  | 10 - 13 | 4 -  8 | `a g A*p !S*p @@`                |10
`SG` | Gaithersburg Troupe     | 10 - 13 | 4 -  8 | `a g A*p S*p @@`                 | 9
`SJ` | Junior Troupe           | 10 - 13 | 4 -  8 | `a g A*p S*p @@`                 | 9
`SB` | Travel Troupe           | 14 - 18 | 1 - 12 | `a A*p`                          |11
`SH` | Shakespeare Troupe      | 14 - 18 | 9 - 12 | `a g A*p @@`                     |12
`SR` | Senior Troupe           | 14 - 18 | 9 - 12 | `a g A*p @@`                     |12
`WN` | Painting Workshop       | 14 - 18 | 1 - 12 | `a`                              | 1
`WP` | Prop Workshop           | 14 - 18 | 1 - 12 | `a`                              | 1
`WW` | Wig Workshop            | 14 - 18 | 1 - 12 | `a`                              | 1
`WX` | Tech Crew Workshop      | 12 - 18 | 1 - 12 | `a`                              | 1
`XA` | Tech Apps               | 12 - 18 | 1 - 12 | `a`                              | 1
`XM` | Makeup Team             | 14 - 18 | 1 - 12 | `a`                              | 1
`XX` | Tech Team               | 12 - 18 | 1 - 12 | `a WX`                           |13

#### Notes:
1. Students need only meet age requirements for Acting classes, Level 1 Tap, Broadway Tap or Broadway Jazz classes, Irish Soft Shoe, Co-ed Jazz &amp; Hip-Hop, Workshops, Tech Apps, or Makeup Team,
2. Students must meet age requirements, and be a girl or boy to be in Broadway Choir or Boy's Jazz &amp; Hip-Hop respectively.
3. Students must meet age requirements, and pass an audition or skill assessment for Level 2 Broadway Tap and Jazz classes.
4. Students must meet age requirements, and be enrolled in at least 1 other class concurrently in order to audition for A Capella Choir.
5. Students who meet age requirements may enroll in Jazz 1 immediately, but students who are 1 year too young may still audition.
6. All students must meet age requirements.  Students who have already taken this class may enroll immediately.  Students who have taken the class 1 level below in the same genre may enroll if they pass an audition.
7. Same as note 6, but previous enrollment in the preceding class's Broadway counterpart is also accepted.
8. Students must meet age requirements, and have taken any Tap, Broadway Tap, or Irish class in the past.
9. Students who meet age and grade requirements, have taken an acting class, and have already been in a troupe, may audition directly for Junior or Gaithersburg Troupe.
10. Students who meet age and grade requirements, and have taken an acting class, but have not been a troupe, may audition jointly for both Junior and Gaithersburg Troupe.
11. Students who meet age requirements, and have taken an Acting class, may enroll in Travel Troupe with no audition necessary.
12. Students who meet age and grade requirements, and have taken an acting class, may audition for Senior or Shakespeare Troupes.
13. Students who meet the age requirements and have taken the Tech Crew Workshop (either this year or in the past) may sign up for the Tech Team.

<!-- `a g A*p S*p @` | Students must meet age and grade requirements, have taken an Acting class, *and* must have already been in a troupe in order to audition for this class.  This is the eligex
`a g A*p !S*p @` | Students must meet age and grade requirements, and have taken an Acting class, but *not* yet been in a troupe
 -->



<!-- A*	Acting Classes
	AA: Acting A
	AB: Acting B
	A0: Showcase Acting Skit #0 (rarely used) (non-enrollable)
	A1: Showcase Acting Skit #1 (non-enrollable)
	A2: Showcase Acting Skit #2 (non-enrollable)
	A3: Showcase Acting Skit #3 (non-enrollable)
	A4: Showcase Acting Skit #4 (non-enrollable)
	A5: Showcase Acting Skit #5 (non-enrollable)
	A6: Showcase Acting Skit #6 (non-enrollable)
	A7: Showcase Acting Skit #7 (non-enrollable)
	A8: Showcase Acting Skit #8 (non-enrollable)
	A9: Showcase Acting Skit #9 (rarely used) (non-enrollable)
	AI: -> SB (former name)
B*	historical
	BT: Ballet (defunct)
C*	Choirs [Note: The numbers 1 and 2 are used instead of A and B, to avoid the counterintuitive situation of having each choir's name begin with the letter from the code of the other choir]
	C1: Broadway Choir
	C2: A Capella Choir
	CH: -> SB (Coffee House)
D*	historical
	DI: Dance Intensive (defunct)
E*	- not used -
F*	Showcase Finale
	FN: Showcase Finale, all performers in Showcase (non-enrollable)
	F0: 12th grade showcase performers who begin the finale (non-enrollable)
	F1: Finale Group #1 (non-enrollable)
	F2: Finale Group #2 (non-enrollable)
	F3: Finale Group #3 (non-enrollable)
	F4: Finale Group #4 (non-enrollable)
	F5: Finale Group #5 (non-enrollable)
	F6: Finale Group #6 (non-enrollable)
	F7: Finale Group #7 (non-enrollable)
	F8: Finale Group #8 (non-enrollable)
	F9: Finale Group #9 (non-enrollable)
	FX: Finale Group #10 (non-enrollable) [Note: Use Roman Numeral X as mnemonic]
	FY: Finale Group #11 (rarely used) (non-enrollable)
	FZ: Finale Group #12 (rarely used) (non-enrollable)
G*	alternate
	GB: -> SG
H*	Dance Class Genre: Jazz/Hip-Hop
	HB: Boys' Jazz & Hip-Hop
	HJ: Jazz & Hip-Hop
I*	Dance Class Genre: Irish Stepdancing
	IS: Irish Soft Shoe
	IH: Irish Hard Shoe
J*	alternate
	JR: -> SJ
K*	- not used -
L*	historic
	LN: Interpretive Sign Language (defunct)
M*	- not used -
N*	- not used -
O*	- not used -
P*	Dance Class Genre: Broadway Tap [Note: Broadway dance codes use last letter of genre]
	P1: Broadway Tap 1
	P2: Broadway Tap 2
Q*	- not used -
R*	- not used -
S*	Acting Troupes & Shows
	SA: Variety Show (Mnemonic: SA = Silent Auction)
	SB: Travel Troupe (Mnemonic: Uhh... Travel Troupe is made of Antimony, right?)
	SC: Showcase
	SG: Gaithersburg Troupe
	SH: Shakespeare Troupe
	SJ: Junior Troupe
	SR: Senior Troupe
T*	alternate
	TT: -> SB
U*	- not used -
V*	Variety Show
	VS: -> SA
W*	One-Time Workshops
	WX: Tech Crew Workshop
	WW: Wig Team Workshop
	WP: Prop Workshop
	WN: Painting Workshop
X*	Tech Program
	XA: Tech Apps
	XM: Make up team
	XX: Tech Team
Y*	- not used -
Z*	Dance Class Genre: Broadway Jazz [ See note at P* ]
	Z1: Broadway Jazz 1
	Z2: Broadway Jazz 2 -->
<!-- 
#name = 'mAcdonald'
#regex = r'(mac)(.+)'
#foo = re.match(regex,name,flags=re.IGNORECASE)
# bar = Each(foo.groups()).title()
# bar = ''.join(bar)
#print bar
print Each([1,2,3,4,5]).__int__ -->