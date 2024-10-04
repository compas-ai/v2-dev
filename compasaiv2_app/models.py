from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timesince import timesince
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg
from django.contrib.postgres.fields import JSONField 
from django.utils.text import slugify
import uuid
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site


def default_booking():
    return [
        {
            "type": "coffee_chat",
            "title": "",
            "start": "",
            "end": "",
            "period": "",
            "mode": "one_time",
            "freq": "",
            "days": [],
            "duration": "",
            "gap": "",
            "time": []
        },
        {
            "type": "office_hours",
            "title": "Sales Workshop",
            "start": "",
            "end": "",
            "period": "",
            "mode": "repeat",
            "freq": "",
            "days": [],
            "duration": "",
            "gap": "",
            "time": []
        },
        {
            "type": "mock_interview",
            "title": "",
            "start": "",
            "end": "",
            "period": "",
            "mode": "one_time",
            "freq": "",
            "days": [],
            "duration": "",
            "gap": "",
            "time": []
        },
        {
            "type": "speed_networking",
            "title": "",
            "start": "",
            "end": "",
            "period": "",
            "mode": "one_time",
            "freq": "",
            "days": [],
            "duration": "",
            "gap": "",
            "time": []
        },
        {
            "type": "check_ins",
            "title": "",
            "start": "",
            "end": "",
            "period": "",
            "mode": "repeat",
            "freq": "",
            "days": [],
            "duration": "",
            "gap": "",
            "time": []
        }
    ]


def default_roadmap():
    return [
            {
            "level": "BEGINNER",
            "startdate": "2024-03-25",
            "sections": [
                {
                    "title": "INTRODUCTION",
                    "id": 1,
                    "duration": "2",
                    "progress": 5,
                    "tasks": [
                        {   
                            "name": "Intro Course",
                            "sub_id": 1,
                            "status": "done",
                            "description": "Click here to start a crash course. This will help you get started in this career path.",
                            "action": "path_courses"
                        },
                        {
                            "name": "Intro Quiz",
                            "sub_id": 2,
                            "status": "pending",
                            "description": "",
                            "action": "roadmap"
                        },
                        {
                            "name": "Your Expectations",
                            "sub_id": 3,
                            "status": "pending",
                            "description": "",
                            "action": "community"
                        }
                    ]
                },
                {
                    "title": "LEARNING",
                    "id": 2,
                    "duration": "6",
                    "progress": 55,
                    "tasks": [
                        {
                            "name": "Beginner Course",
                            "sub_id": 1,
                            "status": "pending",
                            "description": "Spend minimum of 2 hours weekly on a course. ",
                            "action": "path_courses"
   
                        },
                        {
                            "name": "Course Lesson",
                            "sub_id": 2,
                            "status": "pending",
                            "description": "What did you learn from this course?",
                            "action": "community"
                        },
                        
                    ]
                },

                {
                    "title": "PRACTICE",
                    "id": 3,
                    "duration": "2",
                    "progress": 0,
                    "tasks": [
                       
                        {
                            "name": "Project Submission",
                            "sub_id": 1,
                            "status": "pending",
                            "description": "Work on a beginner project",
                            "action": "project"
                        },
                        {
                            "name": "Portfolio Setup",
                            "sub_id": 2,
                            "status": "pending",
                            "description": "Work on a beginner project",
                            "action": "roadmap"
                        },
                        
                    ]
                },
                {
                    "title": "NETWORK",
                    "id": 4,
                    "duration": "1",
                    "progress": 0,
                    "tasks": [
                       
                        {
                            "name": "Book Mentorship",
                            "sub_id": 1,
                            "status": "pending",
                            "description": "Work on a beginner project",
                            "action": "connect_mentors"
                        },
                    ]
                },
            ]
            },
            {
            "level": "INTERMEDIATE",
            "startdate": "2024-09-01",
            "sections": [
                {
                    "title": "APPLICATION",
                    "id": 5,
                    "duration": "15",
                    "progress": 0,
                    "tasks": [
                        {
                            "name": "Open source project",
                            "sub_id": 1,
                            "status": "done",
                            "description": "Build for the public",
                            "action": "project"
                        },
                        {
                            "name": "Internship",
                            "sub_id": 2,
                            "status": "pending",
                            "description": "Apply for internship roles",
                            "action": "roadmap"
                        },
                        {
                            "name": "Share Experience",
                            "sub_id": 3,
                            "status": "pending",
                            "description": "Speak to a mentor",
                            "action": "community"
                        }
                    ]
                },
                
            ]
            },

             {
            "level": "PROFESSIONAL",
            "startdate": "2024-09-01",
            "sections": [
                {
                    "title": "ADVANCED LEARNING",
                    "id": 6,
                    "duration": "8",
                    "progress": 0,
                    "tasks": [
                        {
                            "name": "Start Adavanced Beginner Course",
                            "sub_id": 1,
                            "status": "pending",
                            "description": "Spend minimum of 2 hours weekly on a course. ",
                            "action": "path_courses"
   
                        },
                        {
                            "name": "Course Lesson",
                            "sub_id": 2,
                            "status": "pending",
                            "description": "What did you learn from this course?",
                            "action": "community"
                        },
                        
                    ]
                },
                {
                    "title": "RECOGNITION",
                    "id": 7,
                    "duration": "2",
                    "progress": 0,
                    "tasks": [
                        {
                            "name": "Publication Release",
                            "sub_id": 1,
                            "status": "pending",
                            "description": "Spend minimum of 2 hours weekly on a course. ",
                            "action": "roadmap"
   
                        },
                        {
                            "name": "Certification",
                            "sub_id": 2,
                            "status": "pending",
                            "description": "What did you learn from this course?",
                            "action": "roadmap"
                        },
                        
                    ]
                },

                {
                    "title": "JOB READY",
                    "id": 8,
                    "duration": "4",
                    "progress": 0,
                    "tasks": [
                        {
                            "name": "Mock Interviews",
                            "sub_id": 1,
                            "status": "pending",
                            "description": "Spend minimum of 2 hours weekly on a course. ",
                            "action": "roadmap"
   
                        },
                        {
                            "name": "Job Applications",
                            "sub_id": 2,
                            "status": "pending",
                            "description": "What did you learn from this course?",
                            "action": "roadmap"
                        },
                        
                    ]
                },
                
            ]
            },
            
        ]
class Profile(models.Model):
    FREE = "Free"
    SUBSCRIPTION = "Subscription"

    TIER_CHOICES = (
        (FREE, "Free"),
        (SUBSCRIPTION, "Subscription")
    )

    USER_TYPE = (
        ('', ''),
        ('explorer', 'Explorer'),
        ('seeker', 'Seeker'),
        ('advancer', 'Advancer'),
        ('mentor', 'Mentor')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, choices=USER_TYPE, default='', blank=True)
    is_confirmed = models.BooleanField(default=False)
    is_onboarded = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=10, default=0)
    username = models.CharField(max_length=100, blank=True, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_dp_image', blank=True)
    cover_picture = models.ImageField(upload_to='profile_cover_image', blank=True)
    email = models.EmailField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=100, blank=True)
    joined = models.DateTimeField(default=datetime.now)
    tier = models.CharField(max_length=100, choices=TIER_CHOICES, default=FREE)
    about = models.TextField(blank=True)
    portfolio = models.TextField(blank=True)
    linkedin = models.TextField(blank=True)
    twitter = models.TextField(blank=True)
    facebook = models.TextField(blank=True)
    instagram = models.TextField(blank=True)
    mentor_skill = models.ForeignKey('Skill', on_delete=models.CASCADE, related_name='mentor_skill', null=True, blank=True)
    mentor_booking_info = models.JSONField(default=default_booking, null=True, blank=True)
    strengths = models.JSONField(default=list, null=True, blank=True)
    skills = models.JSONField(default=list, null=True, blank=True)
    education = models.JSONField(default=list, null=True, blank=True)
    experience = models.JSONField(default=list, null=True, blank=True)
    referred_profiles = models.ManyToManyField('Profile', related_name='referred_users', blank=True)
    following = models.ManyToManyField('Profile', related_name='following_users', blank=True)
    followers = models.ManyToManyField('Profile', related_name='followers_users', blank=True)
    resume = models.FileField(upload_to='resumes', blank=True)
    def __str__(self):
        return f"{self.user.username}"
    
    def bio(self):
        # Ensure there's at least one experience entry
        if not self.experience:
            if self.user_type == "mentor":
                return "Professional"
            else:
                return "Beginner"
        
        sorted_experience = sorted(self.experience, key=lambda x: x.get('end_date_raw'), reverse=True)
        most_recent = sorted_experience[0]
        return f"{most_recent.get('title')}, {most_recent.get('company')}"
    
    def connections(self):
        
        ai_username = "compasai"
        profile = Profile.objects.get(username=ai_username)
        following_profiles = self.following.exclude(id=profile.id).exclude(id=self.id)
        follower_profiles = self.followers.exclude(id=profile.id).exclude(id=self.id)
        all_profiles = following_profiles.union(follower_profiles)
        
        return all_profiles
    
    def archived_profiles(self):
        conversations = Conversation.objects.filter(participants=self, archived=True).exclude(messages=None)
        
        profiles_data = []
        for convo in conversations:
            for participant in convo.participants.exclude(id=self.id):
                last_message = convo.messages.order_by('-timestamp').first()
                if last_message:
                    profiles_data.append({
                        'display_name': participant.display_name,
                        'username': participant.username,
                        'profile_picture': participant.profile_picture if participant.profile_picture else None,
                        'last_message': last_message.text,
                        'last_message_time': custom_timesince(last_message.timestamp),
                        'timestamp': last_message.timestamp  # Add the timestamp for sorting
                    })
        
        # Sort profiles_data by 'timestamp', with the most recent message first
        profiles_data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return profiles_data

    def existing_connections(self):
        conversations = Conversation.objects.filter(participants=self).exclude(messages=None).exclude(archived=True)
        
        profiles_data = []
        for convo in conversations:
            if convo.is_group == True:
                try:
                    try:
                        group = Group.objects.get(conversation= convo)
                    except:
                        group = OfficeHour.objects.get(conversation= convo)
                     
                    last_message = convo.messages.order_by('-timestamp').first()
                    unread_messages = 0
                    for message in convo.messages.all():
                        if self not in message.read.all():
                            if message.sender != self:
                                unread_messages += 1

                  
                    if last_message:
                        profiles_data.append({
                            'display_name': group.name,
                            'unread': unread_messages,
                            'is_group': True,
                            'username': group.username,
                            'profile_picture': group.image if group.image else None,
                            'last_message': last_message.text,
                            'last_message_time': custom_timesince(last_message.timestamp),
                            'timestamp': last_message.timestamp  # Add the timestamp for sorting
                        })
                except:
                    pass

            else:
                for participant in convo.participants.exclude(id=self.id):
                    last_message = convo.messages.order_by('-timestamp').first()
                    unread_messages = 0
                    for message in convo.messages.all():
                        if self not in message.read.all():
                            if message.sender != self:
                                unread_messages += 1
                    print(unread_messages)
                    if last_message:
                        profiles_data.append({
                            'display_name': participant.display_name,
                            'unread': unread_messages,
                            'is_group': False,
                            'username': participant.username,
                            'profile_picture': participant.profile_picture if participant.profile_picture else None,
                            'last_message': last_message.text,
                            'last_message_time': custom_timesince(last_message.timestamp),
                            'timestamp': last_message.timestamp  # Add the timestamp for sorting
                        })
                      
       
        # Sort profiles_data by 'timestamp', with the most recent message first
        profiles_data.sort(key=lambda x: x['timestamp'], reverse=True)
  
       
        return profiles_data

    def new_connections(self):
        """
        Returns all other participants' profiles in conversations where this profile is a participant
        and there are no associated messages.

        
        """

        ai_username = "compasai"
        aiprofile = Profile.objects.get(username=ai_username)
        conversations = Conversation.objects.filter(participants=self, messages=None).exclude(archived=True)
        return Profile.objects.filter(participants__in=conversations).exclude(id=self.id).exclude(id=aiprofile.id).distinct()

class Conversation(models.Model):
    participants = models.ManyToManyField('Profile', related_name='participants', blank=True)
    
    is_group = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    messages = models.ManyToManyField('Message', related_name='messages', blank=True)
    removed = models.ManyToManyField('Profile', related_name='removed_participants', blank=True)

    def __str__(self):
        return f"{self.participants.all()}"
    
    def participant_names(self):
        # Assuming the Profile model has a 'name' field
        participants = self.participants.all()
        # Join participant names by commas
        return ', '.join([participant.display_name for participant in participants])

class Message(models.Model):

    MSG_TYPE = (
        ('event', 'Event'),
        ('text', 'Text'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='conversation', null=True)
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    text = models.TextField(blank=False)
    msg_type = models.CharField(max_length=100, choices=MSG_TYPE, default='text', blank=True)
    event = models.JSONField(default=dict, null=True, blank=True)
    images = models.ManyToManyField('PostImage', related_name='message_images', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.ManyToManyField('Profile', related_name='read_messages', blank=True)

    def __str__(self):
        return f"{self.text}"


class Group(models.Model):
    admin = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='group_admin')
    description = models.TextField(blank=True)
    username = models.CharField(max_length=200, blank=False, unique=True)
    name = models.CharField(max_length=200, unique=True, blank=False)
    image = models.ImageField(upload_to='group_images', blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='group_onversation', null=True)
    archived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    path = models.ForeignKey('Skill', on_delete=models.CASCADE, null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.conversation}"
    
    @property
    def url(self):
        current_site = '127.0.0.1:8001'
        url = reverse('message', kwargs={'username': self.username})
        return f'http://{current_site}{url}'
    

class OfficeHour(models.Model):
    admin = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='office_admin')
    path = models.ForeignKey('Skill', on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=True)
    time_slots = models.TextField(blank=True)
    next_schedule = models.JSONField(default=dict)
    schedule = models.JSONField(default=list)
    username = models.CharField(max_length=200, blank=False, unique=True)
    name = models.CharField(max_length=200, unique=True, blank=False)
    image = models.ImageField(upload_to='offcie_images', blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='office_onversation', null=True)
    archived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.conversation}"
    
    @property
    def url(self):
        current_site = '127.0.0.1:8001'
        url = reverse('message', kwargs={'username': self.username})
        return f'http://{current_site}{url}'
    

class RecommenderInfo(models.Model):

    STAGE_TYPE = (
        ('contact', 'Contact'),
        ('description', 'Description'),
        ('status', 'Status'),
        ('hours', 'Hours'),
        ('resources', 'Resources'),
        ('computers', 'Computers'),
        ('strengths', 'Strengths'),
        ('weakness', 'Weakness'),
        ('team', 'Team'),
        ('interests', 'Interests'),
        ('academics', 'Academics'),
        ('exposure', 'Exposure'),
        ('motivation', 'Motivation'),
        ('resume', 'Resume'),
        ('thankyou', 'ThankYou'),
    )

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_recommender')
    stage = models.CharField(max_length=100, choices=STAGE_TYPE, default='contact')
    status = models.BooleanField(default=False)
    skills = models.TextField(blank=True)
    hours = models.IntegerField(default=0)
    resources = models.TextField(blank=True)
    computers = models.TextField(blank=True)
    computers_level = models.IntegerField(default=0)
    strengths = models.TextField(blank=True)
    weakness = models.TextField(blank=True)
    team = models.CharField(max_length=20, blank=False, default="")
    interests = models.TextField(blank=True)
    academics = models.TextField(blank=True)
    exposure = models.TextField(blank=True)
    motivation = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profile.username}"


class Skill(models.Model):
   
    SKILLS_CATEGORY_CHOICES = (
        ("Creative", "Creative"),
        ("Product", "Product"),
        ("Business", "Business"),
        ("Marketing", "Marketing"),
        ("Engineering", "Engineering"),
        ("Data", "Data"),
        ("Operations", "Operations"),
    )

    name = models.CharField(max_length=200, blank=False)
    value = models.CharField(max_length=200, blank=False, default='')
    category = models.CharField(max_length=100, choices=SKILLS_CATEGORY_CHOICES, default=None)
    icon = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}"
    

class MyProfileSkill(models.Model):
    suggested_skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='suggested_skill')
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_profile')
    ranking = models.IntegerField()
    revealed = models.BooleanField(default=False)
    reason = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    progress = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    recommended = models.BooleanField(default=True)
    roadmap = models.JSONField(default=list, null=True, blank=True)

    def __str__(self):
        return f"{self.suggested_skill}"
    
class Community(models.Model):
    name = models.ForeignKey(Skill, on_delete=models.CASCADE)
    posts = models.ManyToManyField('Post', related_name='community_post', blank=True)
    groups =models.ManyToManyField('Group', related_name='community_group', blank=True)
    member = models.ManyToManyField(Profile, related_name='community_member', blank=True)



class PostImage(models.Model):
    image = models.ImageField(upload_to='post_image')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} uploaded at {self.uploaded_at}"

class Post(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    community= models.ForeignKey(Community, on_delete=models.CASCADE, default='')
    post_text = models.TextField()
    images = models.ManyToManyField(PostImage, related_name='post_images', blank=True)
    likes = models.ManyToManyField(Profile, related_name='post_likes', blank=True)
    comments = models.ManyToManyField('Comment', related_name='post_comments', blank=True)
    post_date = models.DateTimeField(default=datetime.now)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    def __str__(self):
        return f"{self.post_text}"
    
    def get_time(self):
        return custom_timesince(self.post_date)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.post_text[:50]}-{uuid.uuid4()}')
        super().save(*args, **kwargs)

    @property
    def url(self):
        current_site = '127.0.0.1:8001'
        url = reverse('view_post', kwargs={'slug': self.slug})
        return f'http://{current_site}{url}'

    
class Comment(models.Model):
    comment_text = models.TextField()
    comment_author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comment_author')
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_post')
    comment_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.comment_text}"
    
    def get_time(self):
        return custom_timesince(self.comment_date)
    

    
class Project(models.Model):
    title = models.TextField()
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='project_images', blank=True)
    tasks = models.JSONField(default=list, null=True, blank=True)
    scenario = models.TextField()
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='project_owner')
    participants = models.ManyToManyField(Profile, related_name='project_participants', blank=True)
    duration = models.IntegerField(default=0)
    submissions = models.ManyToManyField('Submission', related_name='project_submissions', blank=True)


class Submission(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    project= models.ForeignKey(Project, on_delete=models.CASCADE, default='')
    post_text = models.TextField()
    post_link = models.TextField()
    images = models.ManyToManyField(PostImage, related_name='submission_images', blank=True)
    reviews= models.ManyToManyField('Review', related_name='submission_reviews', blank=True)
    post_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.post_text}"
    
    def get_time(self):
        return custom_timesince(self.post_date)
    
    def rating(self):
        average = self.reviews.aggregate(Avg('review_rating'))['review_rating__avg']
        return round(average, 1) if average is not None else 0
    

class Review(models.Model):
    review_text = models.TextField()
    review_rating = models.DecimalField(default=0, max_digits=100, decimal_places=1)
    review_author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='review_author')
    review_submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='review_sub')
    review_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.review_text}"
    
    def get_time(self):
        return custom_timesince(self.review_date)

class Mentorship(models.Model):
    SESSION_TYPE = (
        ('', ''),
        ('coffee_chat', 'coffee_chat'),
        ('office_hours', 'office_hours'),
        ('speed_networking', 'speed_networking'),
        ('mock_interview', 'mock_interview'),
        ('check_ins', 'check_ins'),
    )

    mentor = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='session_mentor')
    learner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='session_learner')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='session_conversation')
    session = models.CharField(max_length=100, choices=SESSION_TYPE, default='', blank=True)
    date_time = models.JSONField(default=list)
    booking_time = models.DateTimeField(default=datetime.now)
    note = models.TextField()


class Booking(models.Model):
    STATUS_TYPE = (
        ('', ''),
        ('upcoming', 'Upcoming'),
        ('completed', 'Completed'),
        ('reschedule', 'Reschedule'),
        ('past', 'Past'),
        ('cancelled', 'Cancelled'),
    )
    session = models.ForeignKey('MentorshipSession', on_delete=models.CASCADE, related_name='booking_session')
    learner =  models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='boooking_learner')
    date = models.DateField()
    start_time = models.TimeField()
    link = models.TextField()
    end_time = models.TimeField()
    note = models.TextField()
    mentor_feedback = models.TextField(blank=True)
    mentor_rating = models.CharField(blank=True, max_length=100)
    learner_feedback = models.TextField(blank=True)
    learner_rating = models.CharField(blank=True, max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_TYPE, default='upcoming', blank=True)
    log = models.JSONField(default=list)
    learner_confirmation = models.BooleanField(default=False)
    mentor_confirmation = models.BooleanField(default=False)



class MentorshipSession(models.Model):
    SESSION_TYPE = (
        ('', ''),
        ('coffee_chat', 'Coffee Chat'),
        ('office_hours', 'Office Hours'),
        ('speed_networking', 'Speed Networking'),
        ('mock_interview', 'Mock Interview'),
        ('check_ins', 'Check Ins'),
    )
    active = models.BooleanField(default=True)
    mentor = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='mentorship_session_mentor')
    session = models.CharField(max_length=100, choices=SESSION_TYPE, default='', blank=True)
    location = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)
    about = models.CharField(max_length=100)
    start_date = models.CharField(max_length=100)
    end_date = models.CharField(max_length=100)
    times = models.JSONField(default=dict)
    link = models.TextField(blank=True)

    @property
    def url(self):
        current_site = '127.0.0.1:8001'
        url = reverse('book_session', kwargs={'username': self.mentor.username})
        return f'http://{current_site}{url}'


def custom_timesince(timestamp):
    now = timezone.now()
    elapsed = now - timestamp

    if elapsed < timedelta(minutes=1):
        # Seconds ago
        seconds = int(elapsed.total_seconds())
        return f"{seconds} seconds ago"
    elif elapsed < timedelta(hours=1):
        # Minutes ago
        minutes = int(elapsed.total_seconds() // 60)
        return f"{minutes} minutes ago"
    elif elapsed < timedelta(hours=24):
        # Hours ago
        hours = int(elapsed.total_seconds() // 3600)
        return f"{hours} hours ago"
    else:
        # More than 24 hours ago, show date
        return timestamp.strftime("%b %d")