# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = false` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Alumnifamily(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    family = models.CharField(max_length=128)
    mfirst = models.CharField(max_length=30)
    mlast = models.CharField(max_length=30)
    mnick = models.CharField(max_length=30)
    ffirst = models.CharField(max_length=30)
    flast = models.CharField(max_length=30)
    fnick = models.CharField(max_length=30)
    joint = models.CharField(max_length=60)
    street = models.CharField(max_length=60)
    apt = models.CharField(max_length=64)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    home = models.CharField(max_length=13)
    mcell = models.CharField(max_length=13)
    fcell = models.CharField(max_length=13)
    email = models.CharField(max_length=128)
    year06 = models.CharField(max_length=10)
    year07 = models.CharField(max_length=10)
    year08 = models.CharField(max_length=10)
    year09 = models.CharField(max_length=10)
    year10 = models.CharField(max_length=10)
    year11 = models.CharField(max_length=10)
    year12 = models.CharField(max_length=10)
    board = models.CharField(max_length=10)
    director = models.CharField(max_length=10)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=128)
    locked = models.CharField(max_length=3)
    policy = models.CharField(max_length=3)
    mailoutfinished = models.CharField(max_length=20)

    class Meta:
        db_table = 'old_alumnifamily'


class Courses(models.Model):
    courseid = models.CharField(unique=True, max_length=6)
    name = models.CharField(max_length=128)
    day = models.CharField(max_length=20)
    start = models.TimeField()
    end = models.TimeField()
    teacher = models.CharField(max_length=30)
    choreographer = models.CharField(max_length=30)
    music = models.CharField(max_length=30)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=25)
    minage = models.IntegerField()
    maxage = models.IntegerField()
    prereq = models.CharField(max_length=30)
    show = models.CharField(max_length=28)
    volhours = models.IntegerField()
    audition = models.CharField(max_length=6)
    creationdate = models.DateField()
    moddate = models.DateTimeField()
    show2 = models.CharField(max_length=30)
    notes = models.CharField(max_length=300)
    active = models.CharField(max_length=3)
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'old_courses'


class ErrorTable(models.Model):
    creationdate = models.DateTimeField()
    errortext = models.TextField()
    page = models.CharField(max_length=128)

    class Meta:
        db_table = 'old_error_table'


class Family(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    family = models.CharField(max_length=128)
    accessid = models.CharField(unique=True, max_length=10)
    mfirst = models.CharField(max_length=30)
    mlast = models.CharField(max_length=30)
    mnick = models.CharField(max_length=30)
    ffirst = models.CharField(max_length=30)
    flast = models.CharField(max_length=30)
    fnick = models.CharField(max_length=30)
    joint = models.CharField(max_length=60)
    street = models.CharField(max_length=60)
    apt = models.CharField(max_length=64)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)
    home = models.CharField(max_length=13)
    mcell = models.CharField(max_length=13)
    fcell = models.CharField(max_length=13)
    email = models.CharField(max_length=128)
    email2 = models.CharField(max_length=128)
    year06 = models.CharField(max_length=10)
    year07 = models.CharField(max_length=10)
    year08 = models.CharField(max_length=10)
    year09 = models.CharField(max_length=10)
    year10 = models.CharField(max_length=10)
    year11 = models.CharField(max_length=10)
    year12 = models.CharField(max_length=10)
    board = models.CharField(max_length=10)
    director = models.CharField(max_length=10)
    password = models.CharField(max_length=256)
    pwd = models.CharField(max_length=256)
    role = models.CharField(max_length=128)
    locked = models.CharField(max_length=3)
    policy = models.CharField(max_length=3)
    mailoutfinished = models.CharField(max_length=20)
    core1 = models.CharField(max_length=128)
    core2 = models.CharField(max_length=128)
    additional = models.TextField()
    gifta = models.TextField()
    giftb = models.TextField()
    skills = models.TextField()
    skillsother = models.CharField(db_column='skillsOther', max_length=128)  # Field name made lowercase.
    tc1 = models.IntegerField()
    tc2 = models.IntegerField()
    exlobby = models.CharField(max_length=3)
    tickets = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        db_table = 'old_family'


class Helptext(models.Model):
    creationdate = models.DateField()
    moddate = models.DateTimeField()
    helpid = models.CharField(max_length=10)
    subject = models.CharField(max_length=64)
    text = models.TextField()

    class Meta:
        db_table = 'old_helptext'


class Invoice(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    familyid = models.CharField(max_length=10)
    paidconfirmed = models.CharField(db_column='PaidConfirmed', max_length=128)  # Field name made lowercase.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    registration = models.CharField(max_length=3)
    showcase = models.CharField(max_length=3)
    sr = models.CharField(max_length=3)
    sh = models.CharField(max_length=3)
    jr = models.CharField(max_length=3)
    gb = models.CharField(max_length=3)
    ch = models.CharField(max_length=3)
    paypalid = models.CharField(max_length=128)

    class Meta:
        db_table = 'old_invoice'


class Mailout(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    title = models.CharField(max_length=20)
    last = models.CharField(max_length=128)
    first = models.CharField(max_length=128)
    address = models.CharField(max_length=128)
    direction = models.CharField(max_length=20)
    address2 = models.CharField(max_length=40)
    street = models.CharField(max_length=20)
    apt = models.CharField(max_length=20)
    city = models.CharField(max_length=128)
    state = models.CharField(max_length=128)
    zip = models.CharField(max_length=128)
    addressfamily = models.CharField(max_length=20)
    family = models.CharField(max_length=128)
    familyid = models.CharField(max_length=20)
    list = models.CharField(max_length=2)

    class Meta:
        db_table = 'old_mailout'


class Paypal(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    token = models.TextField()
    checkoutstatus = models.CharField(max_length=64)
    timestamp = models.CharField(max_length=64)
    correlationid = models.CharField(max_length=64)
    ack = models.CharField(max_length=64)
    version = models.CharField(max_length=64)
    build = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    payerid = models.CharField(max_length=64)
    payerstatus = models.CharField(max_length=64)
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    countrycode = models.CharField(max_length=64)
    shiptoname = models.CharField(max_length=64)
    shiptostreet = models.CharField(max_length=64)
    shiptocity = models.CharField(max_length=64)
    shiptostate = models.CharField(max_length=64)
    shiptozip = models.CharField(max_length=64)
    shiptocountrycode = models.CharField(max_length=64)
    shiptocountryname = models.CharField(max_length=64)
    addressstatus = models.CharField(max_length=64)
    currencycode = models.CharField(max_length=64)
    amt = models.DecimalField(max_digits=10, decimal_places=2)
    itemamt = models.DecimalField(max_digits=10, decimal_places=2)
    invoiceid = models.IntegerField()
    errorcode = models.CharField(max_length=64)
    method = models.CharField(max_length=128)
    pwd = models.CharField(max_length=28)
    signature = models.CharField(max_length=128)
    creditcardtype = models.CharField(max_length=28)

    class Meta:
        db_table = 'old_paypal'


class Registration(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    studentid = models.CharField(max_length=10)
    courseid = models.CharField(max_length=10)
    showcase = models.CharField(max_length=10)
    show = models.CharField(max_length=10)
    noshow = models.CharField(max_length=10)
    entered = models.CharField(max_length=10)
    paid = models.CharField(max_length=64)
    invoiceid = models.IntegerField()

    class Meta:
        db_table = 'old_registration'


class Showcase(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    order = models.IntegerField()
    act = models.CharField(max_length=128)
    course_id = models.CharField(max_length=6)
    notes = models.TextField()

    class Meta:
        db_table = 'old_showcase'


class Student(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    familyid = models.CharField(max_length=64)
    studentid = models.CharField(unique=True, max_length=64)
    first = models.CharField(max_length=64)
    last = models.CharField(max_length=64)
    email = models.CharField(max_length=128)
    sex = models.CharField(max_length=10)
    dob = models.DateField()
    age = models.IntegerField()
    grade = models.CharField(max_length=10)
    tshirt = models.CharField(max_length=10)
    year08 = models.CharField(max_length=10)
    year09 = models.CharField(max_length=10)
    year10 = models.CharField(max_length=10)
    year11 = models.CharField(max_length=10)
    year12 = models.CharField(max_length=10)
    needs = models.CharField(max_length=28)
    needsdescribe = models.TextField()
    def family(self):
        qset = Family.objects.filter(accessid=self.familyid)
        if len(qset):
            return qset[0]
    def __str__(self):
        return ' '.join(['~',self.first,self.last if self.last else self.family().family])

    class Meta:
        db_table = 'old_student'


class VolAssignments(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    family_id = models.CharField(max_length=10)
    vol_jobs_id = models.IntegerField()
    person = models.CharField(max_length=128)
    work_desc = models.TextField()
    hours = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        db_table = 'old_vol_assignments'


class VolCategory(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    category = models.CharField(max_length=128)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'old_vol_category'


class VolCoreJobs(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    job = models.CharField(max_length=128)
    team_id = models.IntegerField()
    core_team = models.IntegerField()
    get_out_jail = models.IntegerField()
    season = models.CharField(max_length=128)
    description = models.TextField()

    class Meta:
        db_table = 'old_vol_core_jobs'


class VolCoreTeam(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    team_id = models.IntegerField()
    team_name = models.CharField(max_length=128)
    description = models.TextField()
    level = models.IntegerField(db_column='Level')  # Field name made lowercase.

    class Meta:
        db_table = 'old_vol_core_team'


class VolGift(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    job = models.CharField(max_length=128)
    team_id = models.IntegerField()
    core_team = models.IntegerField()
    get_out_jail = models.IntegerField()
    season = models.CharField(max_length=128)
    description = models.TextField()

    class Meta:
        db_table = 'old_vol_gift'


class VolGiftFamily(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    vol_giftid = models.IntegerField()
    accessid = models.CharField(max_length=10)
    assigned = models.IntegerField()

    class Meta:
        db_table = 'old_vol_gift_family'


class VolJobs(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    category_id = models.IntegerField()
    team_id = models.IntegerField()
    startdate = models.DateTimeField()
    enddate = models.DateTimeField()
    starttime = models.TimeField()
    endtime = models.TimeField()
    title = models.CharField(max_length=384)
    show = models.CharField(max_length=128)
    description = models.TextField()
    person = models.CharField(max_length=128)
    team_lead = models.CharField(max_length=128)
    cover_hours = models.CharField(max_length=128)
    lobby = models.CharField(max_length=128)
    hours = models.DecimalField(max_digits=11, decimal_places=2)
    numpos = models.IntegerField()
    release = models.CharField(max_length=128)
    lock = models.CharField(max_length=128)
    notes = models.TextField()

    class Meta:
        db_table = 'old_vol_jobs'


class VolSkills(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    skill = models.CharField(max_length=128)
    description = models.TextField()

    class Meta:
        db_table = 'old_vol_skills'


class VolSkillsFamily(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    vol_skillsid = models.IntegerField()
    accessid = models.CharField(max_length=10)
    assigned = models.IntegerField()

    class Meta:
        db_table = 'old_vol_skills_family'


class VolTeam(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    team = models.CharField(max_length=128)
    description = models.TextField()
    level = models.IntegerField(db_column='Level')  # Field name made lowercase.

    class Meta:
        db_table = 'old_vol_team'


class VolTeamFamily(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    vol_teamid = models.IntegerField()
    accessid = models.CharField(max_length=10)
    assigned = models.IntegerField()

    class Meta:
        db_table = 'old_vol_team_family'


class VolTeamHours(models.Model):
    creationdate = models.DateTimeField()
    moddate = models.DateTimeField()
    team_id = models.IntegerField()
    access_id = models.CharField(max_length=10)
    hours = models.FloatField()

    class Meta:
        db_table = 'old_vol_team_hours'
