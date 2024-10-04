from django.contrib import admin

# Register your models here.
from .models import Profile, RecommenderInfo, Skill, MyProfileSkill, Message, Conversation, Mentorship, Group, Project, Community, Post, PostImage, Comment, Submission, Review, OfficeHour, MentorshipSession

admin.site.register(Profile)
admin.site.register(RecommenderInfo)
admin.site.register(Skill)
admin.site.register(MyProfileSkill)
admin.site.register(Message)
admin.site.register(Conversation)
admin.site.register(Mentorship)
admin.site.register(Group)
admin.site.register(Project)
admin.site.register(Community)
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(Comment)
admin.site.register(Submission)
admin.site.register(Review)
admin.site.register(OfficeHour)
admin.site.register(MentorshipSession)
