# HST Website Django Backend
*Technical Documentation & User Guide*

The website is meant to be operable from the client side by someone with only basic computer skills without any User Guide or assistance.  Even so, I'll probably put a general summary as well as some idiosyncracies here.

However, there are a few functions on the admin side that are a little tricky.

##Eligex

This web application can determine whether a given student is eligible for a given course in a given year.  However, due to the complicated nature of the eligibility requirements for many of HST's classes, it was necessary to develop an expression language to determine eligibility of students.  Eligex is a language that in which any requirements and prerequisites for an HST class can be written and will be understood by the server.  It also enables requirements to be written for future classes HST may offer, or to modify the requirements for existing classes, without rewriting the internal code of the website.  It may look daunting, but it's really just boolean algebra (True and False statements).

A line of Eligex is case-sensitive and contains one or more "words", separated by spaces which are converted into True or False values.  Unless trackets (< >) are used, these values will be compiled conjunctively, or AND'ed.  That is to say, if any of the words is False, the expression will return False, and the student will not be eligible for the class.  Only if all the words are True, will the expression return True and the student will be eligible for the class.

### Single-Letter Words
Glyph | Meaning
--- | ---
`#` | Always returns True
`~` | Always returns False
`a` | Returns whether the student meets the age requirements
`g` | Returns whether the student meets the grade requirements (Always returns true if student does not have a `grad_year` listed.  Almost always returns true since most courses are for grades 1-12)
`m` | Male: returns true for boys and false for girls
`f` | Female: returns true for girls and false for boys
`@` | Searches for a *successful* audition or skill assessment for the class by the student
### Single-Letter Modifiers
Glyph | Meaning
--- | ---
`y` | Younger: may be appended to `a` or `g` to relax the *minimum* age or grade requirement by one year for each appended glyph (E. g., If a class is for ages 9-12, `ayy` will return True for 7-12 year olds and False otherwise)
`o` | Older: just like `y` but relaxes the *maximum* age or grade requirement
### Enrollment Search
To require that a student have taken another HST class in order to be eligible for this one, the two-letter ID of the class may be used as an Eligex word (E. g., `J2` will return True for students who are now, or have ever been, enrolled in Jazz 2).  The glyph `*` may be substituted for either character in the ID, and will match any character.  E. g., `*4` will match any Level 4 class and `T*` will match any Tap class (Note: under the current system, `T*` will *not* match Broadway Tap classes, as these begin with `P`)
To further refine these searches, the following modifiers may be appended *after* the class's ID:

Glyph | Meaning
--- | ---
`c` | Will match only *current* enrollments
`p` | Will match only *past* enrollments
`$` | Will match only enrollments for which tuition has been paid
`@` | Will match an audition or skill assessment for the specified course, even if the audition was failed.  (If omitted, word will match only actual enrollments. Not auditions)
`@@`| Will match only a *successful* audition

### Boolean Operators

Glyph | Meaning
--- | ---
Eligex is compiled conjunctively by default.  All words in an expression must be True for the expression to return True.  To modify this, use the following symbols:
`<` `>` | Words within trackets will be evaluated disjunctively, or OR'ed.  The compiler will first evaluate the expression within the trackets to see if *any* of them are true, and if so the entire tracketed expression will be treated as a single True value in the outer expression.  If all of the enclosed words evaluate as False, the tracketed expression will be evaluated as a single False value.
`{` `}` | Braces are evaluated just like trackets, but words within them are AND'ed.  These are useful for nesting inside of trackets (AND within an OR within an AND).  Note that enclosing symbols may not be nested within symbols of the same type.  `< a { T3p @ < P2p T2p > } >` is an invalid expression because it contains trackets within trackets.
`!` | Not: May be appended before a word to return the opposite value

### Examples

Expression | Description
--- | ---
`a g`| Student must meet age and grade requirements.  (Most HST classes have this Eligex)
`a g f` | Student must meet age and grade requirements, and be a girl (This is the eligex for Broadway Choir)
`< J* Z* >` | Student must be enrolled (either now or formerly) an a Jazz or Broadway Jazz Class
`< a { ay @ } >` | Students who meet the age requirement may enroll immediately, but students who are 1 year too young may audition.
`a g < I*p T*p P*p >` | Students must meet age and grade requirements and have formerly taken either an Irish class, or a Tap or Broadway Tap class. (This is the eligex for Irish Hard Shoe)
`a g A*p @` |  Students must meet age and grade requirements, and have taken an Acting class in order to audition (Senior and Shakespeare Troupe)

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