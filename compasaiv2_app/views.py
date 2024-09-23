from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json, time, os, re
from urllib.parse import urlencode
from django.conf import settings
from django.shortcuts import redirect
from .models import User
from django.db.models import Q
from itertools import chain
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Profile, RecommenderInfo, Skill, MyProfileSkill, OfficeHour,  Conversation, Message, Community, Post, PostImage, Comment, Group, Project, Submission, Review, Mentorship
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib import auth
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token, reset_password
from django.contrib.auth.models import User
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string, time, csv, re
import requests
from django.db.models import Count, Max
from django.db.models import OuterRef, Subquery, Max
import ast
import environ
from openai import OpenAI, AzureOpenAI
from django.dispatch import receiver

from datetime import datetime, timedelta
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

#client = OpenAI(api_key=env('OPENAI_API_KEY'))
client = AzureOpenAI(
  azure_endpoint = "https://ai-compasai366216575657.openai.azure.com/", 
  api_key=env('OPENAI_API_KEY'),  
  api_version="2024-02-15-preview"
)

def get_conversation(profile1, profile2):
    # Retrieve all conversations where profile1 is a participant
    conversations = Conversation.objects.filter(participants=profile1)

    # Loop through each conversation and check if profile2 is also a participant
    for convo in conversations:
        if convo.participants.filter(id=profile2.id).exists():
            # Check if there are exactly 2 participants in the conversation
            if convo.participants.count() == 2:
                return convo
    
    # Return None if no conversation with exactly these two participants is found
    return None



@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    print("clicked")
    try:
        profile = Profile.objects.get(user=request.user)
        user_profile = Profile.objects.get(username=username)

        if profile.following.filter(id=user_profile.id).exists():
            # Unfollow action
            profile.following.remove(user_profile)
            user_profile.followers.remove(profile)
            
            convo = get_conversation(profile, user_profile)
            if convo != None:
                convo.archived = True
                convo.save()
                print(":arching")
          
            message = 'unfollow'
        else:
            # Follow action
            profile.following.add(user_profile)
            user_profile.followers.add(profile)
            conver = get_conversation(profile, user_profile)
            if conver == None:
                convo = Conversation.objects.create()
                convo.participants.add(profile)
                convo.participants.add(user_profile)
                print("adding")
            else:
                print("editing")
                conver.archived = False
                conver.save()

            message = 'follow'

        followers = user_profile.followers.all().count()
        return JsonResponse({'message': message, 'count': followers})
        
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def index(request):
    if request.user.is_authenticated == False:
            return redirect('signup')
    #update_skills()

    if Profile.objects.filter(user=request.user).exists() == False:
            print("sjbxsjhb")
            return redirect('onboarding')

    profile = Profile.objects.get(user=request.user)
    print("asjcbjsb")
    if profile.is_onboarded == False and profile.user_type != 'mentor':
       return redirect('onboarding')
    
    is_profile = True
    user_profile = profile
   
    mentors = Profile.objects.filter(user_type='mentor').exclude(id=profile.id)
    peers = Profile.objects.filter(user_type='learner').exclude(id=profile.id)
    recommended_paths = MyProfileSkill.objects.filter(user_profile=profile, recommended=True).order_by('-active','ranking')
    selected_paths = MyProfileSkill.objects.filter(user_profile=profile, recommended=False).order_by('-active','ranking')
    

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('-active','ranking')
    skills = Skill.objects.exclude(id__in=Subquery(my_skills.values('suggested_skill')))

    context = {
        "profile": profile,
        "recommended_paths": recommended_paths,
        "selected_paths": selected_paths,
        "mentors": mentors,
        "is_profile": is_profile,
        "user_profile": user_profile,
        "active_path": active_path,
        'skills': skills
    }
    return render(request, 'home.html', context)

@csrf_exempt
def profile(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
   
    strengths = []
    if profile.strengths:
        strengths = json.loads(profile.strengths)
   
    education = profile.education
    experience = profile.experience

    is_profile = False
    user_profile = Profile.objects.get(username=username)

    mentors = Profile.objects.filter(user_type='mentor').exclude(id=profile.id)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    if user_profile == profile:
        is_profile= True
    context = {
        "profile": profile,
        "strengths": strengths,
        "user_profile": user_profile,
     

        "mentors": mentors,
      
        "experiences": experience,
        "education": education,
        "is_profile": is_profile,
        "active_path": active_path
    }
    return render(request, 'profile_about.html', context)

@csrf_exempt
def profile_projects(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    is_profile = False
    user_profile = Profile.objects.get(username=username)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    if user_profile == profile:
        is_profile= True
    context = {
        "profile": profile,
        "user_profile": user_profile,
        "is_profile": is_profile,
        "active_path": active_path

    }
    return render(request, 'profile_projects.html', context)

@csrf_exempt
def profile_skills(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    skills = [
        {
            "name": "Python",
            "progress": "79%"
        },
        {
            "name": "Javascript",
            "progress": "65%"
        },
        {
            "name": "Canva",
            "progress": "70%"
        }
    
    ]
    # if profile.skills:
    #     skills = json.loads(profile.skills)
    is_profile = False
    user_profile = Profile.objects.get(username=username)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    if user_profile == profile:
        is_profile= True
    context = {
        "profile": profile,
        "user_profile": user_profile,
        "is_profile": is_profile,
        "skills": skills,
        "active_path": active_path

    }
   
    return render(request, 'profile_skills.html', context)

@csrf_exempt
def remove_overlay(request, username):
    print("oakakk")
    return HttpResponse("")


@csrf_exempt
def remove_overlay_book(request, username):
    print("oakakk")
    return HttpResponse("")

@csrf_exempt
def profile_paths(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    recommended_paths = MyProfileSkill.objects.filter(user_profile=profile, recommended=True).order_by('-active','ranking')
    selected_paths = MyProfileSkill.objects.filter(user_profile=profile, recommended=False).order_by('-active','ranking')

    is_profile = False
    user_profile = Profile.objects.get(username=username)

    if user_profile == profile:
        is_profile= True

    
    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    
    context = {
        "profile": profile,
        "user_profile": user_profile,
        "recommended_paths": recommended_paths,
        "selected_paths": selected_paths,
        "is_profile": is_profile,
        "active_path": active_path
    }
    return render(request, 'profile_paths.html', context)

@csrf_exempt
def profile_paths_view(request, username, skill):
    if request.user.is_authenticated == False:
            return redirect('signup')
    if request.method == 'POST':
        print("NA  a dey work")
        if request.user.is_authenticated == False:
                return redirect('signup')
        profile = Profile.objects.get(user=request.user)
        is_profile = False
        user_profile = Profile.objects.get(username=username)
        skill_item = Skill.objects.get(name=skill)
        my_skill = MyProfileSkill.objects.get(user_profile=profile, suggested_skill=skill_item)

        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)


        if user_profile == profile:
            is_profile= True
        context = {
            "profile": profile,
            "user_profile": user_profile,
            "is_profile": is_profile,
            "skill": my_skill,
            "active_path": active_path
        }
        return render(request, 'path-overlay.html', context)
    else:
        print("NA  bb dey work")
        if request.user.is_authenticated == False:
                return redirect('signup')
        profile = Profile.objects.get(user=request.user)
        is_profile = False
        user_profile = Profile.objects.get(username=username)
        skill_item = Skill.objects.get(name=skill)
        my_skill = MyProfileSkill.objects.get(user_profile=profile, suggested_skill=skill_item)
        my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')


        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

        if user_profile == profile:
            is_profile= True
        context = {
            "profile": profile,
            "user_profile": user_profile,
            "is_profile": is_profile,
            "skill": my_skill,
            "my_skills": my_skills,
            "active_path": active_path
        }
        return render(request, 'path-overlay-direct.html', context)

@csrf_exempt
def update_profile_data(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        try:

            if request.POST.get('type') == "BIO":
                name = request.POST.get('name')
                about = request.POST.get('about')
                profile.display_name = name
                profile.about = about

                profile.save()
            if request.POST.get('type') == "SKILLS":
                skills = request.POST.get('skills')
                profile.strengths = skills
                profile.save()

            if request.POST.get('type') == "LINKS":
                profile.portfolio = request.POST.get('portfolio')
                profile.linkedin = request.POST.get('linkedin')
                profile.instagram = request.POST.get('instagram')
                profile.twitter = request.POST.get('twitter')
                profile.facebook = request.POST.get('facebook')
                
                profile.save()

            if request.POST.get('type') == "EDUCATION":
                if request.POST.get('subtype') == "ADD":
                    education = profile.education
                    item = {}
                    item["id"] = len(education) + 1
                    item['school'] = request.POST.get('school')
                    item['degree']= request.POST.get('degree')
                    item['start_date_raw'] = request.POST.get('start_date')
                    item['end_date_raw'] = request.POST.get('end_date')
                    date_obj = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d")
                    formatted_start_date = date_obj.strftime("%b %Y")
                    date_obj = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d")
                    formatted_end_date = date_obj.strftime("%b %Y")
                    item['start_date'] = formatted_start_date
                    item['end_date'] = formatted_end_date

                    education.append(item)
                    profile.education = education
                
                    profile.save()
                elif request.POST.get('subtype') == "UPDATE":
                    education = profile.education
                    id = int(request.POST.get('id'))
                    item = []
                    for it in education:
                        if it['id'] == id:
                            item = it
                            break

                    education.remove(item)

                    
                    
                    item["id"] = id
                    item['school'] = request.POST.get('school')
                    item['degree']= request.POST.get('degree')
                    print(request.POST.get('start_date'))
                    print(request.POST.get('end_date'))
                    if request.POST.get('start_date'):
                        print(request.POST.get('start_date'))
                        item['start_date_raw'] = request.POST.get('start_date')
                        date_obj = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d")
                        formatted_start_date = date_obj.strftime("%b %Y")
                        item['start_date'] = formatted_start_date

                    if request.POST.get('end_date'):
                        print(request.POST.get('end_date'))
                        item['end_date_raw'] = request.POST.get('end_date')
                        
                        date_obj = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d")
                        formatted_end_date = date_obj.strftime("%b %Y")
                        
                        item['end_date'] = formatted_end_date

                    education.append(item)
                    profile.education = education
                
                    profile.save()

                elif request.POST.get('subtype') == "DELETE":
                    education = profile.education
                    id = int(request.POST.get('id'))
                    item = []
                    for it in education:
                        if it['id'] == id:
                            item = it
                            break

                    education.remove(item)
                    profile.education = education
                
                    profile.save()
            if request.POST.get('type') == "EXPERIENCE":
                if request.POST.get('subtype') == "ADD":
                    experience = profile.experience
                    item = {}
                    item["id"] = len(experience) + 1
                    item['title'] = request.POST.get('title')
                    item['company']= request.POST.get('company')
                    item['description']= request.POST.get('description')
                    item['start_date_raw'] = request.POST.get('start_date')
                    item['end_date_raw'] = request.POST.get('end_date')
                    date_obj = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d")
                    formatted_start_date = date_obj.strftime("%b %Y")
                    date_obj = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d")
                    formatted_end_date = date_obj.strftime("%b %Y")
                    item['start_date'] = formatted_start_date
                    item['end_date'] = formatted_end_date

                    experience.append(item)
                    profile.experience = experience
                
                    profile.save()
                elif request.POST.get('subtype') == "UPDATE":
                    experience = profile.experience
                    id = int(request.POST.get('id'))
                    item = []
                    for it in experience:
                        if it['id'] == id:
                            item = it
                            break

                    experience.remove(item)
   
                    item["id"] = id
                    item['title'] = request.POST.get('title')
                    item['company']= request.POST.get('company')
                    item['description']= request.POST.get('description')
                    if request.POST.get('start_date'):
                        print(request.POST.get('start_date'))
                        item['start_date_raw'] = request.POST.get('start_date')
                        date_obj = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d")
                        formatted_start_date = date_obj.strftime("%b %Y")
                        item['start_date'] = formatted_start_date

                    if request.POST.get('end_date'):
                        print(request.POST.get('end_date'))
                        item['end_date_raw'] = request.POST.get('end_date')
                        
                        date_obj = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d")
                        formatted_end_date = date_obj.strftime("%b %Y")
                        
                        item['end_date'] = formatted_end_date

                    experience.append(item)
                    profile.experience = experience
                
                    profile.save()

                elif request.POST.get('subtype') == "DELETE":
                    experience = profile.experience
                    id = int(request.POST.get('id'))
                    item = []
                    for it in experience:
                        if it['id'] == id:
                            item = it
                            break

                    experience.remove(item)
                    profile.experience = experience
                
                    profile.save()

        except Exception as e:
            print(e)

        return JsonResponse({'message': 'Profile changes saved successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def update_profile_images(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    if request.method == 'POST':
        user_profile = Profile.objects.get(user=request.user)
            # Handle profile picture
        try:
            if 'dp' in request.FILES:
                # Delete the old profile picture if it exists
                if user_profile.profile_picture:
                    if os.path.isfile(user_profile.profile_picture.path):
                        os.remove(user_profile.profile_picture.path)
                
                # Save the new profile picture
                user_profile.profile_picture = request.FILES['dp']

            # Handle cover picture
            if 'cover' in request.FILES:
                # Delete the old cover picture if it exists
                if user_profile.cover_picture:
                    if os.path.isfile(user_profile.cover_picture.path):
                        os.remove(user_profile.cover_picture.path)
                
                # Save the new cover picture
                user_profile.cover_picture = request.FILES['cover']

            user_profile.save()
        except Exception as e:
            print(e)

        return JsonResponse({'message': 'Profile changes saved successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def enrol_path_loader(request, username, skill):
    return render(request, 'path_enroll_loader.html', {"skill":skill, "username": username}) 


@csrf_exempt
def enrol_path(request, username, skill):
    if request.user.is_authenticated == False:
            return redirect('signup')
    time.sleep(2)
    profile = Profile.objects.get(username=username)
    skilitem = Skill.objects.get(value=skill)
    if MyProfileSkill.objects.filter(user_profile=profile, active=True):
        all_skills = MyProfileSkill.objects.filter(user_profile=profile, active=True)
        for item in all_skills:
            item.active = False
            item.save()
    if MyProfileSkill.objects.filter(user_profile=profile, suggested_skill=skilitem):
        active_skill = MyProfileSkill.objects.get(user_profile=profile, suggested_skill=skilitem)
        active_skill.active = True
        community = Community.objects.get(name=active_skill.suggested_skill)
        community.member.add(profile)
        active_skill.save()
    else:
        reason = "You selected this skill"
        new_skill = MyProfileSkill.objects.create(user_profile=profile, suggested_skill=skilitem, reason=reason, active=True, ranking=10, recommended=False)
    return redirect('path_detail', skill)


@csrf_exempt
def profile_edit_bio(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')

    is_profile = False
    user_profile = Profile.objects.get(username=username)
    profile_type = "BIO"


    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)


    if user_profile == profile:
        is_profile = True
    else:
        return redirect('index')
    
    context = {
        "profile": profile,
        "user_profile": user_profile,
        "my_skills": my_skills,
        "is_profile": is_profile,
        "profile_type": profile_type,
        "active_path": active_path
    }
    if request.method == 'GET':
        return render(request, 'profile_edit_direct.html', context)
    else:
        return render(request, 'profile_edit.html', context)

@csrf_exempt
def profile_edit_skills(request, username):
    soft_skills = ["Communication","Teamwork","Problem-Solving","Adaptability","Critical Thinking","Creativity","Time Management","Attention to Detail","Leadership","Collaboration","Emotional Intelligence","Conflict Resolution","Decision Making","Organizational Skills","Interpersonal Skills","Negotiation","Project Management","Analytical Thinking","Innovation","Stress Management","Presentation Skills"]
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')
    profile_type = "SKILLS"
    is_profile = False
    user_profile = Profile.objects.get(username=username)
    strengths = []
    if profile.strengths:
        strengths = json.loads(profile.strengths)
    if user_profile == profile:
        is_profile = True
    else:
        return redirect('index')
    
    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    
    context = {
        "profile": profile,
        "user_profile": user_profile,
        "my_skills": my_skills,
        "is_profile": is_profile,
        "profile_type": profile_type,
        "soft_skills": soft_skills,
        "strengths": strengths,
        "active_path": active_path

    }
    if request.method == 'GET':
        return render(request, 'profile_edit_direct.html', context)
    else:
        return render(request, 'profile_edit.html', context)


@csrf_exempt
def profile_edit_links(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')

    is_profile = False
    user_profile = Profile.objects.get(username=username)


    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)


    if user_profile == profile:
        is_profile = True
    else:
        return redirect('index')
    
    profile_type = "LINKS"
    
    context = {
        "profile": profile,
        "user_profile": user_profile,
        "my_skills": my_skills,
        "is_profile": is_profile,
        "profile_type": profile_type,
        "active_path": active_path
    }
    if request.method == 'GET':
        return render(request, 'profile_edit_direct.html', context)
    else:
        return render(request, 'profile_edit.html', context)

@csrf_exempt
def profile_edit_education(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')


    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)


    is_profile = False
    user_profile = Profile.objects.get(username=username)

    if user_profile == profile:
        is_profile = True
    else:
        return redirect('index')
    
    profile_type = "EDUCATION"
   

    context = {
        "profile": profile,
        "user_profile": user_profile,
        "my_skills": my_skills,
        "is_profile": is_profile,
        "profile_type": profile_type,
        "education": profile.education,
        "active_path": active_path
    }
    if request.method == 'GET':
        return render(request, 'profile_edit_direct.html', context)
    else:
        return render(request, 'profile_edit.html', context)

@csrf_exempt
def profile_edit_experience(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')


    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)


    is_profile = False
    user_profile = Profile.objects.get(username=username)

    if user_profile == profile:
        is_profile = True
    else:
        return redirect('index')
    
    profile_type = "EXPERIENCE"

    context = {
        "profile": profile,
        "user_profile": user_profile,
        "my_skills": my_skills,
        "is_profile": is_profile,
        "profile_type": profile_type,
        "experiences": profile.experience,
        "active_path": active_path
    }
    if request.method == 'GET':
        return render(request, 'profile_edit_direct.html', context)
    else:
        return render(request, 'profile_edit.html', context)

@csrf_exempt
def profile_edit_settings(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')


    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)


    is_profile = False
    user_profile = Profile.objects.get(username=username)

    if user_profile == profile:
        is_profile = True
    else:
        return redirect('index')
    
    profile_type = "SETTINGS"
    
    context = {
        "profile": profile,
        "user_profile": user_profile,
        "my_skills": my_skills,
        "is_profile": is_profile,
        "profile_type": profile_type,
        "active_path": active_path
    }
    return render(request, 'profile_edit.html', context)

@csrf_exempt
def set_password(request):
    context = {
                    "stage": 'PASSWORD',
                    "set_password": True
                }
    return render(request, 'signup.html', context)

@csrf_exempt
def confirm_email(request, email):
    user = User.objects.get(email=email)
    send_activation_email(request, user, email)
    context = {
                    "stage": 'CONFIRM',
                    "set_password": False
                }
    return render(request, 'signup.html', context)

@csrf_exempt
def signup(request):
    stage = "EMAIL"

    if request.user.is_authenticated == True:
        stage = "PASSWORD"
        print("hasbvhasshsbvhsbhsbhsnhsbsbsh")
        profile = Profile.objects.get(user=request.user)
        if profile.is_confirmed == False:
            print("na her shaaaa")
            stage = "CONFIRM"
            user = request.user
            send_activation_email(request, user, user.email)
        
        else:
            print("e reach here oooo")
            if request.user.check_password('12345') == False:
                return redirect('onboarding')
           

    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        ref_code = request.POST.get('ref_code', '')
        
        if(email):
            print(email)
            stage = "EMAIL"
            password = '12345'
            username, host= email.split('@') 
            username = re.sub(r'[^\w]', '_', username)
            if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                if Profile.objects.filter(email=email).exists() == False:
                        user = User.objects.get(Q(username=username) | Q(email=email))
                        profile = Profile.objects.get(user=user)
                        user_auth = auth.authenticate(username=email, password=password)
                        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        try:
                            ref_profile = Profile.objects.get(referral_code=ref_code)
                            ref_profile.referred_profiles.add(profile)
                            ref_profile.save()
                            print(ref_profile)
                            send_referral_reward_email(request, ref_profile.user, ref_profile.username, username, email)
                            send_activation_email(request, user, email)
                            
                        except:
                            ref_profile = None
                            #send_activation_email(request, user, email)
                            #return JsonResponse({'message': 'activate'})
                            pass
                        stage = "PASSWORD"
                else:
                    pass
                    
            else:
                if Profile.objects.filter(username=username).exists() == True:
                    code = generate_code()
                    print(code)
                    username = username + "-" + code
                user = User.objects.create_user(username=username, password=password, email=email)
                profile = Profile.objects.get(user=user)
                user_auth = auth.authenticate(username=email, password=password, backend='django.contrib.auth.backends.ModelBackend')
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                try:
                    ref_profile = Profile.objects.get(referral_code=ref_code)
                    ref_profile.referred_profiles.add(profile)
                    ref_profile.save()
                    print(ref_profile)
                    send_referral_reward_email(request, ref_profile.user, ref_profile.username, username, email)
                    send_activation_email(request, user, email)
                    
                except:
                    profile.is_confirmed = True
                    profile.save()
                    #send_activation_email(request, user, email)
                    #return JsonResponse({'message': 'activate'})
                    
                stage = "CONFIRM"
        elif(password):
            stage = "PASSWORD"
            print(password)
            if request.user.is_authenticated:
                if request.user.check_password('12345'):
                    request.user.set_password(password)
                    request.user.save()
                    print("password changed")
                    update_session_auth_hash(request, request.user)
                    return redirect('onboarding')
                else:
                    return redirect('onboarding')
            else:
                # Handle the case for unauthenticated users, like redirecting to login or displaying a message
                return redirect('login')
               
    context = {
                    "stage": stage,
                    "set_password": False
                }
    return render(request, 'signup.html', context)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_item = User.objects.get(email=email)
        except:
            user_item = None
    
        user = auth.authenticate(username=user_item.username, password=password, backend='django.contrib.auth.backends.ModelBackend')
        if user is not None:
            profile = Profile.objects.get(user=user)
            if not profile.is_confirmed:
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return JsonResponse({'wrong': True, 'reason': 'Please confirm your email', 'no_password': False, 'is_confirmed': True, 'email': email})
            elif not profile.is_onboarded:
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return JsonResponse({'onboarding': True})
            else:
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return JsonResponse({'index': True})
        elif User.objects.filter(email=email).exists():
            user_prof = User.objects.get(email=email)
            profile = Profile.objects.get(user=user_prof)
            if profile.is_confirmed == False:
                auth.login(request, user_prof, backend='django.contrib.auth.backends.ModelBackend')
                return JsonResponse({'wrong': True, 'reason': 'Please confirm your email', 'no_password': False, 'is_confirmed': True, 'email': email})
            elif user_prof.check_password('12345'):
                auth.login(request, user_prof, backend='django.contrib.auth.backends.ModelBackend')
                return JsonResponse({'wrong': True, 'reason': 'Password has not been set for this account', 'no_password': True, 'is_confirmed': False})
            else:
               
                return JsonResponse({'wrong': True, 'reason': 'Password is incorrect.', 'no_password': False, 'is_confirmed': False})

    return render(request, 'login.html')

@csrf_exempt
def check_email_exists(request):
    email = request.POST.get('email', None)
    empty = False
    exists = User.objects.filter(email=email).exists()
    if email == "" or email == None:
        empty = True
    return JsonResponse({'exists': exists, 'empty': empty})



@csrf_exempt
def onboarding(request):
    #fields = ["Graphics Design","Web Design","Motion Graphics","Animation","Video Editing","Content Writing","Content Creation","Product Design","Product Management","Scrum Management","Product Marketing","Business Analysis","Business Intelligence","Business Analytics","Business Development","Financial Analysis","Legal and Compliance","Customer Relationship Management (CRM)","Digital Marketing","Content Marketing","Public Relations (PR)","Community Management","Game Development","Mobile App Development","Database Management","Frontend Development","Backend Development","Fullstack Development","Blockchain Development","Trading Algorithm Development","Quality Assurance","Cloud & DevOps","Cybersecurity","Data Analysis","Data Analytics","Data Science","Data Engineering","Artificial Intelligence","Project Management","IT Administration","Customer Support","Virtual Assistant"]
    fields =  ["C", "C++", "C#", "Java", "Ruby", "Perl", "Objective-C", "TypeScript", "Scala", "Rust", "Haskell", "Elixir", "Erlang", "Lua", "Julia", "Fortran", "COBOL", "Lisp", "Scheme", "Racket", "F#", "Dart", "VHDL", "Verilog", "Assembly", "Bash", "PowerShell", "Tcl", "Groovy", "OCaml", "Ada", "MATLAB", "Vala", "Crystal", "Nim","Adobe Photoshop", "Adobe Illustrator", "CorelDRAW", "Affinity Designer", "Inkscape", "GIMP", "Sketch", "Figma", "Canva", "Adobe InDesign", "Adobe XD", "Webflow", "Wix", "WordPress", "Bootstrap", "Tailwind CSS", "Elementor", "Squarespace", "Adobe After Effects", "Blender", "Cinema 4D", "Nuke", "Autodesk Maya", "Houdini", "Mocha Pro", "DaVinci Resolve", "HitFilm Pro", "Red Giant Suite", "Toon Boom Harmony", "Adobe Animate", "TVPaint", "Moho", "Dragonframe", "Pencil2D", "Krita", "Adobe Premiere Pro", "Final Cut Pro", "Sony Vegas", "Avid Media Composer", "iMovie", "HitFilm Express", "Filmora", "Lightworks", "Shotcut", "Grammarly", "Hemingway Editor", "Google Docs", "Microsoft Word", "Scrivener", "ProWritingAid", "Quillbot", "Evernote", "Notion", "Contentful", "Adobe Spark", "Lumen5", "Animoto", "Crello", "Piktochart", "Desygner", "Stencil", "Snappa", "Kapwing", "InVision", "Axure RP", "Marvel App", "Proto.io", "Framer", "Balsamiq", "Zeplin", "Jira", "Trello", "Asana", "ClickUp", "Monday.com", "Wrike", "Aha!", "ProductPlan", "Smartsheet", "Scrumwise", "Zoho Sprints", "Targetprocess", "VersionOne", "Assembla", "Kanbanize", "VivifyScrum", "HubSpot", "Marketo", "Pardot", "Mailchimp", "SEMrush", "Hootsuite", "Buffer", "Google Analytics", "BuzzSumo", "Ahrefs", "Microsoft Excel", "Google Sheets", "Tableau", "Microsoft Power BI", "QlikView", "SAP BusinessObjects", "SAS Business Intelligence", "IBM Cognos", "Oracle BI", "TIBCO Spotfire", "Domo", "Looker", "Sisense", "Zoho Analytics", "Google Data Studio", "Alteryx", "R", "Python", "SPSS", "Qlik Sense", "Salesforce", "Zoho CRM", "LinkedIn Sales Navigator", "Outreach", "Pipedrive", "ActiveCampaign", "Salesloft", "Drift", "Gong.io", "QuickBooks", "Xero", "Bloomberg Terminal", "Sage Intacct", "SAP FICO", "Oracle Financials", "LexisNexis", "Westlaw", "iManage", "NetDocuments", "Clio", "Relativity", "MyCase", "Everlaw", "Onit", "ContractSafe", "Microsoft Dynamics 365", "Nimble", "Freshsales", "SugarCRM", "Insightly", "Keap", "Sprout Social", "Moz", "PRWeb", "Agility PR", "Prowly", "BuzzStream", "CoverageBook", "Newswire", "Prezly", "Mention", "Discord", "Slack", "Facebook Groups", "Discourse", "Vanilla Forums", "Tribe", "Mighty Networks", "Unity", "Unreal Engine", "Godot", "CryEngine", "GameMaker Studio", "Construct 3", "RPG Maker", "Cocos2d", "Lumberyard", "Stencyl", "Android Studio", "Xcode", "React Native", "Flutter", "Ionic", "Swift", "Kotlin", "Firebase", "PhoneGap", "Apache Cordova", "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle DB", "Microsoft SQL Server", "Redis", "Amazon RDS", "Cassandra", "HTML", "CSS", "JavaScript", "React.js", "Vue.js", "Angular", "Sass", "Webpack", "Node.js", "Django", "Flask", "Ruby on Rails", "Spring Boot", "Express.js", "Laravel", "ASP.NET", "PHP", "Go", "Next.js", "Ethereum", "Solidity", "Truffle", "Hyperledger", "Corda", "Quorum", "Remix IDE", "Ganache", "OpenZeppelin", "Hardhat", "MQL4", "Pine Script", "MetaTrader", "TradingView", "NinjaTrader", "QuantConnect", "cTrader", "Amibroker", "MultiCharts", "AlgoTrader", "Selenium", "Postman", "TestRail", "BrowserStack", "QTest", "Cucumber", "Appium", "Zephyr", "SoapUI", "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Jenkins", "Ansible", "Puppet", "Nagios", "Wireshark", "Kali Linux", "Splunk", "Nmap", "Metasploit", "Snort", "Tenable", "Burp Suite", "OpenVAS", "Nessus", "Stata", "TensorFlow", "Keras", "PyTorch", "SciKit-Learn", "Pandas", "NumPy", "Matplotlib", "Apache Spark", "Kafka", "Hadoop", "AWS Glue", "Airflow", "Flink", "Snowflake", "DBT", "Google BigQuery", "OpenAI GPT", "Google AI Platform", "Amazon SageMaker", "H2O.ai", "IBM Watson", "Basecamp", "Microsoft Project", "SolarWinds", "Zabbix", "Zendesk", "Freshdesk", "Intercom", "Help Scout", "LiveAgent", "Zoho Desk", "HubSpot Service Hub", "Kayako", "Salesforce Service Cloud", "HappyFox", "Zoom", "Google Calendar", "Microsoft Teams", "Calendly", "Zapier"]

    resources = ["Mobile Phone","Laptop","Desktop","Tablet","Ipad"]
    soft_skills = ["Communication","Teamwork","Problem-Solving","Adaptability","Critical Thinking","Creativity","Time Management","Attention to Detail","Leadership","Collaboration","Emotional Intelligence","Conflict Resolution","Decision Making","Organizational Skills","Interpersonal Skills","Negotiation","Project Management","Analytical Thinking","Innovation","Stress Management","Presentation Skills"]
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        profile = None
    stage = "CONTACT"
    new_comment = ""
    
    info = {}
    stage_dict= get_stage_dict(stage)
   
    if request.user.is_authenticated == True:
        try:
            profile = Profile.objects.get(user=request.user)
            info = RecommenderInfo.objects.get(profile=profile)
            stage_dict = get_adjacent_stage(str(info.stage).upper(), "NEXT")
            stage = info.stage
            if profile.is_onboarded or profile.user_type == 'mentor':
                return redirect('index')
        except:
            pass
    else:
        return render(request, 'login.html')
    
    stage = stage_dict['stage']
    if request.method == 'POST':
        
        action = request.POST.get('action', '')
        stage = request.POST.get('stage', '')
        value = request.POST.get('value', '')
        stage_dict = get_adjacent_stage(stage, action)

        question_dict = get_stage_dict(stage)

        if (action == "NEXT") and stage != "NAME" and stage != "EMAIL":
            question = question_dict['question']
            user_message = value
            next_message_raw = stage_dict['question']

            format_new_message = [{
                "role": "system", 
                "content": f'''
                    Context
                    ---------------
                    You are an expert AI psychometrist who provides follow up comments after users answer questions about their personality, strengths, academic background, resources and motivation to curate the most appropriate technology career path for them.
                    
                    Task
                    ---------------
                    1. Using the listed rules below, generate the 1 sentence response about the previous question and answer to continue the conversation
                    2. Use the previous question and answer to generate a comment.
                    3. Write the comment in a fun and engaging way that persnalised the experience. 

                    Rules
                    ---------------
                    * The comment should ALWAYS be personal, simple and direct
                    * The entire comment should be 10 words or less
                    * The entire comment should be a single sentence
                    * The entire comment should be WORDS or NUMBERS only, no special characters.
                    * If no provided answer or unclear answer to asked question, do not ask user to repeat or clarify.

                    Parameters
                    ---------------
                    - Asked Question: {question}
                    - Provided Answer: {user_message}
                '''
            }]

            completion = client.chat.completions.create(
                    model='gpt-35-turbo',
                    messages=format_new_message,
                    temperature=0.7,
                    max_tokens=800,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None
                )
            #print(completion)
            new_comment = completion.choices[0].message.content
        print(new_comment)
        if stage == "CONTACT":
            profile_data = json.loads(value)
            
            # Access individual values from the dictionary
            name = profile_data.get('name', '')
            email = profile_data.get('email', '')
            phone = profile_data.get('phone', '')

            password = "12345"
            username, host= email.split('@') 
            username = re.sub(r'[^\w]', '_', username)
            if User.objects.filter(Q(username=username) | Q(email=email)).exists():
                if Profile.objects.filter(email=email).exists() == False:
                        profile = Profile.objects.create(user=user, username=username, phone_number=phone, email=email, display_name=name )
                        return JsonResponse({'error': 'User already exists. Please proceed to login'}, status=400)
                else:
                    profile = Profile.objects.get(user=request.user)
                    profile.display_name = name
                    profile.phone_number = phone
                    profile.save()
                    user_auth = auth.authenticate(username=email, password=password)
                    auth.login(request, user_auth, backend='django.contrib.auth.backends.ModelBackend')
            else:
                if Profile.objects.filter(username=username).exists() == True:
                    code = generate_code()
                    print(code)
                    username = username + "-" + code
                user = User.objects.create_user(username=email, password=password, email=email)
                profile = Profile.objects.create(user=user, username=username, phone_number=phone, email=email, display_name=name )
                user_auth = auth.authenticate(username=email, password=password)
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                send_activation_email(request, user, email)
                stage = "NAME"

        elif stage == "DESCRIPTION":
            try:
                info = RecommenderInfo.objects.get(profile=profile)
            except:
                if value == "learner":
                    print("ahsbchasbchasbashh")
                    info = RecommenderInfo.objects.create(profile=profile, stage = stage.lower())
            profile.user_type = str(value)
            profile.save()
            print(profile.user_type)
            
        elif stage == "STATUS":
            try:
                info = RecommenderInfo.objects.get(profile=profile)
            except:
                info = RecommenderInfo.objects.create(profile=profile, stage = stage.lower())
            if value:
                info.stage = stage.lower()
                info.status = True
                info.skills = value
                profile.skills = value
                info.save()
                profile.save()

        elif stage == "HOURS":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.hours = value
                info.save()
        elif stage == "RESOURCES":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.resources = value
                info.save()

        elif stage == "COMPUTERS":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                print(value)
                info.stage = stage.lower()
                value_to_name = {
                    0: 'Beginner',
                    1: 'Novice',
                    2: 'Intermediate',
                    3: 'Advanced',
                    4: 'Expert',
                }
                name = value_to_name.get(int(value))
                info.computers = name
                info.computers_level = int(value)
                
                info.save()

            print(info.computers)
                

        elif stage == "STRENGTHS":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.strengths = value
                info.save()

        elif stage == "WEAKNESS":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.weakness = value
                info.save()
        
        elif stage == "TEAM":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.team = value
                info.save()

        elif stage == "INTERESTS":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.interests = value
                info.save()

        elif stage == "ACADEMICS":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.academics = value
                info.save()

        elif stage == "EXPOSURE":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.exposure = value
                info.save()

        elif stage == "MOTIVATION":
            info = RecommenderInfo.objects.get(profile=profile)
            if value:
                info.stage = stage.lower()
                info.motivation = value
                info.save()  

        elif stage == "THANKYOU":
            pass
   
    try:
        skills_list = ast.literal_eval(info.skills)
        if isinstance(skills_list, list):
            skills_list = skills_list
    except:
        skills_list = []
    levels = ['Beginner', 'Novice', 'Intermediate', 'Advanced', 'Expert']
    stage_percent = str(int(get_stage_percent(stage_dict['stage']))) + "%"

    if new_comment != "":    
        stage_dict['comment'] =new_comment
    context = {
        "stage": stage_dict,
        'skills_json': json.dumps(fields),
        "resources": resources,
        "strengths": soft_skills,
        "weaknesses": soft_skills,
        "stage_percent": stage_percent,
        "profile": profile,
        "info": info ,
        "levels": levels,
        'skills_list': skills_list
    }
    print(skills_list)
    return render(request, 'onboarding.html', context)



@csrf_exempt
def recommendation(request):
            print("loadingnggg")
            stage = {}

            #ogun_fields = ["Audio Production", "Mobile Photography", "Graphics Design",  "Web Design", "Web3 & Blockchain", "Content Writing", "Motion Graphics",  "Social Media Management", "Data Analysis"]
            username = None
            if request.method == 'POST':
                print("sedfiksedfikd")
                fields = ["Graphics Design","Web Design","Motion Graphics","Animation","Video Editing","Content Writing","Content Creation","Product Design","Product Management","Scrum Management","Product Marketing","Business Analysis","Business Intelligence","Business Development","Financial Analysis","Legal and Compliance","Customer Relationship Management (CRM)","Digital Marketing","Content Marketing","Public Relations (PR)","Community Management","Game Development","Mobile App Development","Database Management","Frontend Development","Backend Development","Fullstack Development","Blockchain Development","Trading Algorithm Development","Quality Assurance","Cloud & DevOps","Cybersecurity","Data Analysis","Data Science","Data Engineering","Artificial Intelligence","Project Management","IT Administration","Customer Support","Virtual Assistant"]
                if request.user.is_authenticated == False:
                        return redirect('signup')
                else:
                    print("afhdfsd")
                    try:
                        profile = Profile.objects.get(user=request.user)
                        info = RecommenderInfo.objects.get(profile=profile)
                                
                        summary_message = [{
                            "role": "system", 
                            "content": f'''
                                Context
                                --------
                                You are an expert AI psychometrist who summarizes user profile information about their personality, strengths, academic background, resources and motivation. This summary needs to elavate & highlight key information that would be helpful choosing a career in tech.
                                
                                Task
                                --------
                                1. Using the listed rules below, summarise the user's psychometric traits.
                                2. Use the below parameters as information for the summary
                                3. Only Highlight key information that can steer the path of user's career, good or bad. 
                                4. Personalise the summary by using user's name that will be provided in the parameter

                                
                                Parameters
                                ---------
                                - User's name is {profile.display_name}
                                - Question: What are your existing tech skills.  Answer: {info.skills}
                                - Question: How many hours a week? Weekly availability to learn and practice. Answer: {info.hours}
                                - Question: Which resources can you have access to? Answer: {info.resources}
                                - Question: How proficient are you with computers? Answer: {info.computers}
                                - Question: What are your top strengths? Answer: {info.strengths}
                                - Question: What are your top weaknesses? Answer: {info.weakness}
                                - Question: Do you prefer working in a team or alone? Answer: {info.team}
                                - Question: Tell me about how you spend your free time. Answer: {info.interests}
                                - Question: Tell me about your academic background. Answer: {info.academics}
                                - Question: Do you have any prior exposure to technology? {info.exposure}
                                - Question: ⁠What is your motivation to acquire a tech skill? {info.motivation}


                                Rules
                                --------
                                * Address user by name.
                                * The summary must contain key information that can help user's career decision. 
                                * The entire comment should be 50 words or less
                                * The entire comment should be a single paragraph only.
                                * The entire comment should be WORDS or NUMBERS only, no special characters.
                                * The output should just be the summary no titles, headers , dictionaries, lists. Just the summary.
                                * Do not give any advice, just summarise. 
                                

                            '''
                        }]

                        summary_completion = client.chat.completions.create(
                                model='gpt-35-turbo',
                                messages=summary_message,
                                temperature=0.7,
                                max_tokens=800,
                                top_p=0.95,
                                frequency_penalty=0,
                                presence_penalty=0,
                                stop=None
                            )
                        summary = summary_completion.choices[0].message.content
                        print(summary)
                        profile.about = summary
                        profile.save()

                        print("etjetg")

                        recommendation_message = [{
                            "role": "system", 
                            "content": f'''
                                Context
                                --------
                                You are an expert AI psychometrist recommender who recommends tech skills that fit the user's psychometric summary. The summary contains user profile information about their personality, strengths, academic background, resources, and motivation. This summary will be used to choose possible careers in tech for the user.
                                
                                Task
                                --------
                                1. Using the listed rules below, recommend the top 3 tech skills that fit the user's information listed in the below parameters
                                2. Choose the top 3 recommended skills from the provided Skills List only; do not change any words.
                                3. Provide a reason each recommended skill fits the user.
                                4. Personalise the reason by using user's name.

                                Parameters
                                ---------
                                - User's name is {profile.display_name}
                                - Question: What are your existing tech skills.  Answer: {info.skills}
                                - Question: How many hours a week? Weekly availability to learn and practice. Answer: {info.hours}
                                - Question: Which resources can you have access to? Answer: {info.resources}
                                - Question: How proficient are you with computers? Answer: {info.computers}
                                - Question: What are your top strengths? Answer: {info.strengths}
                                - Question: What are your top weaknesses? Answer: {info.weakness}
                                - Question: Do you prefer working in a team or alone? Answer: {info.team}
                                - Question: Tell me about how you spend your free time. Answer: {info.interests}
                                - Question: Tell me about your academic background. Answer: {info.academics}
                                - Question: Do you have any prior exposure to technology? {info.exposure}
                                - Question: ⁠What is your motivation to acquire a tech skill? {info.motivation}

                                Skills List
                                ---------
                                Below is the list of skills to choose from. ONLY CHOOSE FROM THIS LIST AND RETURN THE EXACT WORD. 
                                {fields}

                                Decision Factors
                                --------------
                                The factors below are ranked according to importance in the recommendation decision process. The top-ranked factors should be considered first using the corresponding percentage of importance.
                                - Existing Skills  - 25%
                                - Academic Background - 20%
                                - Available Time and Resources -15%
                                - Computer Exposure and Proficiency - 10%
                                - Interests and Motivation - 15%
                                - Strengths & Weaknesses - 10%
                                - Working in a Team - 5%

                                Rules
                                --------
                                * Select only 3 of the most fitting tech skills for the user's psychometric traits.
                                * Use the top-ranking factors to make a decision about the recommendations.
                                * Choose the top 3 recommendations from the Skills List above ONLY.
                                * Return output in the JSON format specified below.
                                * Reason for each skill should be 20 words or less
                                * Personalise the reason by using user's name.

                                Output Format
                                --------
                                Your response should be in the following JSON format:

                                [
                                    {{
                                        "ID": <ID>,
                                        "skill": "<skill>",
                                        "reason": "<reason>"
                                    }},
                                    {{
                                        "ID": <ID>,
                                        "skill": "<skill>",
                                        "reason": "<reason>"
                                    }},
                                    {{
                                        "ID": <ID>,
                                        "skill": "<skill>",
                                        "reason": "<reason>"
                                    }}
                                ]
                            '''
                        }]


                        recommendation_completion = client.chat.completions.create(
                                model='gpt-35-turbo',
                                messages=recommendation_message,
                                temperature=0.7,
                                max_tokens=800,
                                top_p=0.95,
                                frequency_penalty=0,
                                presence_penalty=0,
                                stop=None
                            )
                        recommendation = recommendation_completion.choices[0].message.content
                        data = json.loads(recommendation)

                        if MyProfileSkill.objects.filter(user_profile=profile).exists():
                            old_skills = MyProfileSkill.objects.filter(user_profile=profile)
                            old_skills.delete()

                        for dat in data:
                            get_skill = Skill.objects.get(name=dat['skill'])
                            my_skill = MyProfileSkill.objects.create(suggested_skill=get_skill, user_profile=profile,  reason=dat['reason'], ranking=dat['ID'])
                            my_skill.save()
                            
                        profile.is_onboarded = True
                        profile.save()

                        my_skill = MyProfileSkill.objects.filter(user_profile=profile)[0]
                        username = profile.username

                        print(recommendation)

                        stage['stage'] = "RESULTS"
                        context = {
                            "profile": profile,
                            "my_skill": my_skill,
                            "stage": stage,
                            "username" : profile.username,
                            "fields": fields
                        }
                        time.sleep(5)
                        return redirect('index')
                    except Exception as e:
                        print("qwfghvqafq qwfyhgqfe")
                        print(e)
                        stage = {}
                        stage['stage'] = "THANKYOU"
                        context = {
                            "stage": stage,
                            
                        }
                        return render(request, 'onboarding.html', context)
            stage['stage'] = "THANKYOU"
            profile = Profile.objects.get(user=request.user)
            my_skill = MyProfileSkill.objects.filter(user_profile=profile).first()
            context = {
                            "stage": stage,
    
                        }
            return render(request, 'onboarding.html', context)

@csrf_exempt
def logout(request):
    auth.logout(request)
    return redirect('index')

@csrf_exempt
def connect(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    mentors = Profile.objects.filter(user_type='mentor').exclude(id=profile.id)
    peers = Profile.objects.filter(user_type='learner').exclude(id=profile.id)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    context = {
        "profile": profile,
        "mentors":  mentors,
        "peers": peers,
        "active_path": active_path
    }
    return render(request, 'connect_mentors.html', context)

@csrf_exempt
def connect_peers(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    mentors = Profile.objects.filter(user_type='mentor').exclude(id=profile.id)
    peers = Profile.objects.filter(user_type='learner').exclude(id=profile.id)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    

    context = {
        "profile": profile,
        "mentors":  mentors,
        "peers": peers,
        "active_path": active_path
    }
    return render(request, 'connect_peers.html', context)

@csrf_exempt
def connect_mentors(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    mentors = Profile.objects.filter(user_type='mentor').exclude(id=profile.id)
    peers = Profile.objects.filter(user_type='learner').exclude(id=profile.id)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    context = {
        "profile": profile,
        "mentors":  mentors,
        "peers": peers,
        "active_path": active_path
    }
    return render(request, 'connect_mentors.html', context)

@csrf_exempt
def connect_all(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    return render(request, 'connect_all.html')


def get_time_slots():
    # Generate all time slots from 12 AM to 12 Midnight
    start_time = datetime.strptime('00:00', '%H:%M')
    end_time = datetime.strptime('23:59', '%H:%M')
    time_slots = []

    current_time = start_time
    while current_time <= end_time:
        time_slots.append(current_time.strftime('%I:%M %p'))  # 12-hour format with AM/PM
        current_time += timedelta(hours=1)

    return time_slots


def get_booking():
    types = ['cafe', 'office_hours', 'mock interview', 'networking', 'check ins']
    return [{"type": "coffee_chat","title": "","start": "2024-09-23 23:00","end": "2024-12-23","period": "8","mode": "one_time","freq": "4","days": ['Monday', 'Tuesday', 'Wednesday'],"duration": "30m","gap": '30m',"time": ['12:00 AM', '1:00 AM', '05:00 PM']},{"type": "office_hours","title": "","start": "2024-09-23 23:00","end": "2024-12-23","period": "8","mode": "repeat","freq": "4","days": ['Saturday', 'Sunday'],"duration": "1h","gap": '30m',"time": ['03:00 AM', '09:00 AM', '05:00 PM']},{"type": "mock_interview","title": "","start": "2024-09-23 23:00","end": "2024-12-23","period": "8","mode": "one_time","freq": "2","days": ['Tuesday', 'Sunday'],"duration": "1h","gap": '30m',"time": ['05:00 AM', '09:00 AM', '05:00 PM']},{"type": "speed_networking","title": "","start": "2024-09-23 23:00","end": "2024-12-23","period": "8","mode": "one_time","freq": "4","days": ['Tuesday', 'Wednesday'],"duration": "1h","gap": '30m',"time": ['08:00 AM', '09:00 AM', '05:00 PM']},{"type": "check_ins","title": "","start": "2024-09-23 23:00","end": "2024-12-23","period": "8","mode": "repeat","freq": "4","days": ['Friday', 'Wednesday'],"duration": "1h","gap": '30m',"time": ['05:00 AM', '09:00 AM', '05:00 PM']}]



def get_booked_sessions(mode, freq, date, time):
    # Parse the given date
    session_date = date  # assuming date is in 'YYYY-MM-DD' format
    session_time = time  # time is already in correct format (e.g., '3:00 PM')
    
    # If the mode is 'one_time', return the date and time directly
    if mode == 'one_time':
        return [{'date': session_date.strftime('%Y-%m-%d'), 'time': session_time}]

    # If the mode is 'repeat', calculate the recurring sessions
    elif mode == 'repeat':
        freq = int(freq)  # Frequency in weeks
        session_day = session_date.weekday()  # Get the weekday of the given date
        booked_sessions = []

        # Loop to calculate future session dates based on the frequency
        for i in range(freq):
            future_date = session_date + timedelta(weeks=i)
            booked_sessions.append({'date': future_date.strftime('%Y-%m-%d'), 'time': session_time})
        
        return booked_sessions

    return []


def get_booked_sessions_for_mentor(mentor):
    # Filter the Mentorship objects where the mentor is the specified mentor
    bookings = Mentorship.objects.filter(mentor=mentor)
    
    # Create a list to hold all the booked sessions with their dates and times
    booked_sessions = []

    for booking in bookings:
        booking_date_times = booking.date_time  # This is the list of date_time in the JSONField

        # Iterate over all date_time entries in the JSONField
        for entry in booking_date_times:
            # Extract the date and time from the entry
            date_str = entry.get('date')
            time_str = entry.get('time')
            
            # If date is not in the correct format, handle the conversion
            try:
                # Convert the date to a datetime object for easier formatting
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                # Handle the error if date_str is not in the expected format
                date_obj = None
            
            # Append the session details to the list
            booked_sessions.append({
               
                'date': date_str,
                'time': time_str
            })
    
    return booked_sessions

@csrf_exempt
def confirm_booking(request):
    if request.method == 'POST':
        session = request.POST.get('type', '')
        mode = request.POST.get('mode', '')
        freq = request.POST.get('freq', '')
        date_str = request.POST.get('date', '')
        date = datetime.strptime(date_str, '%Y-%m-%d')
        time = request.POST.get('time', '')
        note = request.POST.get('note', '')
        mentor_username = request.POST.get('username', '')

        print(mentor_username, session, mode, freq, date, time, note)
            
        mentor = Profile.objects.get(username=mentor_username)
        profile = Profile.objects.get(user=request.user)

        conver = get_conversation(profile, mentor)
        if conver == None:
            convo = Conversation.objects.create()
            convo.participants.add(profile)
            convo.participants.add(mentor)
            
            text = f"Hi {mentor.display_name}, I just booked a {session} session with you for {date.strftime('%A, %B %d, %Y')} at {time}. Looking forward to our chat! Talk to you soon!"
            msg = Message.objects.create(conversation=convo, sender=profile, text=text)
            convo.messages.add(msg)
            conver = convo
        else:
            text = f"Hi {mentor.display_name}, I just booked a {session} session with you for {date.strftime('%A, %B %d, %Y')} at {time}. Looking forward to our chat! Talk to you soon!"
            msg = Message.objects.create(conversation=conver, sender=profile, text=text)
            conver.messages.add(msg)

        date_list = get_booked_sessions(mode, freq, date, time)
        print(date_list)

        mentorship = Mentorship.objects.create(conversation=conver, mentor=mentor, learner=profile, session=session, note=note, date_time=date_list)

        return JsonResponse({'message': mentor.username})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def view_calendar(request):
    try:
        if request.method == 'POST':
            session = request.POST.get('session', '')
            mentor_username = request.POST.get('username', '')
            print(session,mentor_username)
            mentor = Profile.objects.get(username=mentor_username)
            booking_info = mentor.mentor_booking_info
            booking_data = next(sess for sess in booking_info if sess['type'] == session)
            booked_data = get_booked_sessions_for_mentor(mentor)
            print(booked_data)
            return JsonResponse({'booking_data': booking_data, 'booked_data': booked_data})
    except Exception as e:
        return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def book_session(request, username):
    if request.user.is_authenticated == False:
            return redirect('signup')
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        user_profile = Profile.objects.get(username=username)
        mentors = Profile.objects.filter(user_type='mentor').exclude(id=profile.id)
        peers = Profile.objects.filter(user_type='learner').exclude(id=profile.id)
         # Example unavailable times
        unavailable_time = ['08:00 AM', '09:00 AM', '05:00 PM']
        time_slots = get_time_slots()

        

        available_times = [time for time in time_slots if time not in unavailable_time]
        is_profile = False

        if user_profile == profile:
            is_profile= True


        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
        context = {
            "profile": profile,
            "user_profile": user_profile,
            "is_profile": is_profile,
            "mentors":  mentors,
            "peers": peers,
            "active_path": active_path
        }
        return render(request, 'book_session.html', context)
    else:
        profile = Profile.objects.get(user=request.user)
        user_profile = Profile.objects.get(username=username)
        mentors = Profile.objects.filter(user_type='mentor').exclude(id=profile.id)
        peers = Profile.objects.filter(user_type='learner').exclude(id=profile.id)
        unavailable_time = ['08:00 AM', '09:00 AM', '05:00 PM']
        time_slots = get_time_slots()
        available_times = [time for time in time_slots if time not in unavailable_time]
        is_profile = False

        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

        if user_profile == profile:
            is_profile= True
        context = {
            "profile": profile,
            "user_profile": user_profile,
            "is_profile": is_profile,
            "mentors":  mentors,
            "peers": peers,
            "active_path": active_path,
            "available_times": available_times
        }
        return render(request, 'book_session_direct.html', context)

@csrf_exempt
def path(request):
    if request.user.is_authenticated == False:
            return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('-active','ranking')
    skills = Skill.objects.exclude(id__in=Subquery(my_skills.values('suggested_skill')))
    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    context = {
        "profile": profile,
        "my_skills": my_skills,
        "skills": skills,
        "active_path": active_path
       
    }
    return render(request, 'path.html', context)

@csrf_exempt
def path_detail(request, skill_name):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    skill = Skill.objects.get(value=skill_name)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    if  MyProfileSkill.objects.filter(suggested_skill=skill, user_profile=profile).exists():
        path = MyProfileSkill.objects.get(suggested_skill=skill, user_profile=profile)
    else:
        path = None

    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')
    skills = Skill.objects.all()[:12]
    peers = Profile.objects.filter(user_type='learner').exclude(id=profile.id)
    print(peers)
    context = {
        "path": path,
        "profile": profile,
        "my_skills": my_skills,
        "skills": skills,
        "skill": skill,
        "peers": peers,
        "active_path": active_path
    }
    return render(request, 'path_detail-about.html', context)

@csrf_exempt
def path_courses(request, skill_name):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    skill = Skill.objects.get(value=skill_name)
    
    path = MyProfileSkill.objects.get(suggested_skill=skill, user_profile=profile)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')
    skills = Skill.objects.all()[:12]

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    context = {
        "path": path,
        "profile": profile,
        "my_skills": my_skills,
        "skills": skills,
        "active_path": active_path
    }
    return render(request, 'path_detail-courses.html', context)

@csrf_exempt
def path_mentors(request, skill_name):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    skill = Skill.objects.get(value=skill_name)
    path = MyProfileSkill.objects.get(suggested_skill=skill, user_profile=profile)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')
    skills = Skill.objects.all()[:12]
    mentors = Profile.objects.filter(user_type='mentor').exclude(id=profile.id)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    context = {
        "path": path,
        "profile": profile,
        "my_skills": my_skills,
        "skills": skills,
        "mentors": mentors,
        "active_path": active_path
    }
    return render(request, 'path_detail-mentors.html', context)
@csrf_exempt
def path_projects(request, skill_name):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    skill = Skill.objects.get(value=skill_name)
    path = MyProfileSkill.objects.get(suggested_skill=skill, user_profile=profile)
    my_skills = MyProfileSkill.objects.filter(user_profile=profile).order_by('ranking')
    skills = Skill.objects.all()[:12]

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    context = {
        "path": path,
        "profile": profile,
        "my_skills": my_skills,
        "skills": skills,
        "active_path": active_path
    }
    return render(request, 'path_detail-projects.html', context)

@csrf_exempt
def all_messages(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        message_status = 'All'

        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            
        context = {
                "profile": profile,
                "message_status": message_status,
                 "active_path": active_path
            }
        return render(request, 'all_messages.html', context)
    else:
        return redirect('message', profile.username )


@csrf_exempt
def archive_message(request, username):
    if request.user.is_authenticated == False:
        return redirect('signup')

    profile = Profile.objects.get(user=request.user)
    try:
        
        user_profile = Profile.objects.get(username=username)
        is_group = request.POST.get('is_group', '')

        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

        if is_group == "True":
            group = Group.objects.get(username=username)
            conver = group.conversation
            is_group = True
        else:
            user_profile = Profile.objects.get(username=username)
            conver = get_conversation(profile, user_profile)
            is_group = False
        if conver != None:
            if conver.archived == True:
                conver.archived = False
                conver.save()
                message_status = 'Archive'
                print("removed archived")


                context = {
                    "profile": profile,
                    "message_status": message_status,
                    "is_group": is_group, 
                    "active_path": active_path
                }
                return render(request, 'archived.html', context)
            else:
                conver.archived = True
                conver.save()
                print("added archive")
                message_status = 'All'
                context = {
                    "profile": profile,
                    "message_status": message_status,
                    "is_group": is_group,
                     "active_path": active_path
                }
                return render(request, 'all_messages.html', context)
        
    except Exception as e:
        print(e)
        message_status = 'All'
        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
        context = {
            "profile": profile,
            "message_status": message_status,
             "active_path": active_path
        }
        return render(request, 'all_messages.html', context)

@csrf_exempt
def clear_unread(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username', '')
            is_group = request.POST.get('is_group', '')
            print(username)
            profile = Profile.objects.get(user=request.user)

            if is_group == "True":
                group = Group.objects.get(username=username)
                conversation = group.conversation
            else:
                user_profile = Profile.objects.get(username=username)
                conversation = get_conversation(profile, user_profile)
            chat_messages = conversation.messages.all().order_by('-timestamp')


           
            for message in chat_messages:
                if message.read == False:
                    if message.sender != profile:
                        message.read = True
                        message.save()
                        print("removingnnn")
                       
            return HttpResponse("")
    except Exception as e:
        print(e)
        return HttpResponse("")

@csrf_exempt
def delete_message(request, username):
    if request.user.is_authenticated == False:
        return redirect('signup')
    try:
        profile = Profile.objects.get(user=request.user)
        user_profile = Profile.objects.get(username=username)
        is_group = request.POST.get('is_group', '')
        
        if is_group == "True":
            group = Group.objects.get(username=username)
            conver = group.conversation
            is_group = True
        else:
            user_profile = Profile.objects.get(username=username)
            conver = get_conversation(profile, user_profile)
            is_group = False
        if conver != None:
            messages = conver.messages.all()
            messages.delete()
            message_status = 'All'

            active_path = None
            if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
                active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            context = {
                "profile": profile,
                "message_status": message_status,
                "is_group": is_group,
                "active_path": active_path
            }
            return render(request, 'all_messages.html', context)
        
    except Exception as e:
        print(e)
        message_status = 'All'
        context = {
            "profile": profile,
            "message_status": message_status
        }
        return render(request, 'all_messages.html', context)

@csrf_exempt
def add_participant(request, group, username):
    
    try:
        try:
            group = Group.objects.get(username=group)
        except:
            group = OfficeHour.objects.get(username=group)
        
        profile = Profile.objects.get(user=request.user)
        convo = group.conversation
        participant = Profile.objects.get(username=username)
        convo.participants.add(profile)
        


        event =  {
            "action": "add",
            "user_1": profile.display_name,
            "user_2": participant.display_name,
            "timestamp": datetime.now().isoformat()
        }
        msg = Message.objects.create(conversation=convo, sender=profile, text="", msg_type='event', event=event)
        msg.read.add(profile)
        convo.messages.add(msg)

        return HttpResponse('Please wait...')
    
    except Exception as e:
        print(e)
        return HttpResponse('Unable to process your request.')
    


@csrf_exempt
def remove_participant(request, group, username):
    try:
        group = Group.objects.get(username=group)
    except:
        group = OfficeHour.objects.get(username=group)
    profile = Profile.objects.get(user=request.user)
    convo = group.conversation
    participant = Profile.objects.get(username=username)

    if participant != profile and participant != group.admin:
        convo.participants.remove(participant)
        convo.removed.add(participant)
        
        event =  {
            "action": "remove",
            "user_1": profile.display_name,
            "user_2": participant.display_name,
            "timestamp": datetime.now().isoformat()
        }
        msg = Message.objects.create(conversation=convo, sender=profile, text="", msg_type='event', event=event)
        msg.read.add(profile)
        convo.messages.add(msg)
        convo.removed.add(participant)
        return HttpResponse("<p> You removed this user.</p>")   

    elif profile == participant and profile == group.admin:
        group.deleted = True
        group.save()
        event =  {
            "action": "delete",
            "user_1": profile.display_name,
            "user_2": participant.display_name,
            "timestamp": datetime.now().isoformat()
        }

        msg = Message.objects.create(conversation=convo, sender=profile, text="", msg_type='event', event=event)
        msg.read.add(profile)
        convo.messages.add(msg)
        
        return HttpResponse("<p> You deleted this group.</p>")  

    elif profile == participant:
        convo.participants.remove(participant)
        convo.removed.add(participant)
        event =  {
            "action": "left",
            "user_1": profile.display_name,
            "user_2": participant.display_name,
            "timestamp": datetime.now().isoformat()
        }
         
        msg = Message.objects.create(conversation=convo, sender=profile, text="", msg_type='event', event=event)
        msg.read.add(profile)
        convo.messages.add(msg)
        convo.removed.add(participant)
        return HttpResponse("<p> You left this group.</p>")   
    return HttpResponse('')   


@csrf_exempt
def archived(request):
    if request.user.is_authenticated == False:
            return redirect('signup')
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        message_status = 'Archive'

        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            
        context = {
                "profile": profile,
                "message_status": message_status,
                "active_path": active_path
            }
        return render(request, 'archived.html', context)
    else:
        return redirect('message', profile.username )
    
@csrf_exempt
def messaging(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    message_item = False
    ai_username = "compasai"
    aiprofile = Profile.objects.get(username=ai_username)
    user_profile = None

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
    
    context = {
        "profile": profile,
        "messages": message_item,
        "aiprofile": aiprofile,
        "user_profile": user_profile,
        "active_path": active_path
    }
    return render(request, 'messages.html', context)

@csrf_exempt
def new_chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('text', '')
        username = request.POST.get('username', '')
        is_group = request.POST.get('is_group', '')
        profile = Profile.objects.get(user=request.user)
        user_profile = None

        if is_group == "True":
            try:
                group = Group.objects.get(username=username)
            except:
                group = OfficeHour.objects.get(username=username)
            conversation = group.conversation
        else:
            user_profile = Profile.objects.get(username=username)
            conversation = get_conversation(profile, user_profile)

        images = []
        image_urls = []

        # Retrieve all images
        for key in request.FILES:
            if key.startswith('images_'):  # Assuming images are sent with keys 'images_0', 'images_1', etc.
                uploaded_image = request.FILES[key]
                images.append(uploaded_image)

      
        comm_message = Message.objects.create(conversation=conversation, text=user_message, sender=profile)
        for image in images:
            new_image = PostImage.objects.create(image=image)
            comm_message.images.add(new_image)
            image_urls.append(new_image.image.url)
        
        conversation.messages.add(comm_message)
        comm_message.save()

        dp = ''
        if profile.profile_picture:
            dp = profile.profile_picture.url

        return JsonResponse({'message': 'success', 'time': timezone.now().strftime("%I:%M %p"), 'images': image_urls, 'id':comm_message.id , 'dp':dp})
    else:
        return JsonResponse({'message': 'error', 'error': 'Invalid request method'})


def parse_timestamp(item):
    if hasattr(item, 'timestamp'):
        # Convert to naive datetime if the object is timezone-aware
        if item.timestamp.tzinfo is not None:
            return item.timestamp.replace(tzinfo=None)
        return item.timestamp
    else:
        # For events, ensure the parsed timestamp is naive
        dt = datetime.fromisoformat(item['timestamp'])
        if dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt
@csrf_exempt
def message(request, username):
    if request.user.is_authenticated == False:
        return redirect('signup')
    try:
        if request.method == 'POST':
            is_group_val = request.POST.get('type', '')
            is_group = "False"
            is_office = False
            in_session = False
            conversation = None

            combined = []
            message_item = True
            profile = Profile.objects.get(user=request.user)
            message_status = 'All'
            user_profile = None
            aiprofile = None
            group = None

            try:
                user_profile = Profile.objects.get(username=username)
                ai_username = "compasai"
                aiprofile = Profile.objects.get(username=ai_username)
                ai_conversation = get_conversation(profile, user_profile)
                if user_profile == aiprofile:
                    if ai_conversation == None:
                        convo = Conversation.objects.create()
                        convo.participants.add(profile)
                        convo.participants.add(aiprofile)
                conversation = get_conversation(profile, user_profile)
                chat_messages = conversation.messages.all().order_by('timestamp')
            except:
                try:
                    group = Group.objects.get(username=username)
                except:
                    group = OfficeHour.objects.get(username=username)

                print(group)
                conversation = group.conversation
                chat_messages = conversation.messages.all().order_by('timestamp')
                print("done")
                is_group = "True"

            else:
                pass

            today = datetime.now().date()
            yesterday = today - timedelta(days=1)

            active_path = None
            if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
                active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

            # Count unread messages
            unread_messages = 0
            first_message = 0
            for message in chat_messages:
                if message.read == False:
                    if message.sender != profile:
                        if first_message == 0:
                            first_message = message.pk
                        unread_messages += 1
            print("done tooo")
            context = {
                "profile": profile,
                "messages": message_item,
                "user_profile": user_profile,
                "message_status": message_status,
                "aiprofile": aiprofile,
                "chat_messages": chat_messages,
                "today": today,
                "yesterday" : yesterday,
                "today_str": str(today),
                "yesterday_str" : str(yesterday),
                'unread_messages':unread_messages,
                "first_message": first_message,
                "is_group": is_group,
                "group": group,
                "username": username,
                "combined": combined,
                "is_office": is_office,
                "in_session": in_session,
                "conversation": conversation,
                "active_path": active_path
            }
            return render(request, 'message_detail.html', context)
   
        else:
            
            message_item = True
            conversation = None
            combined = []
            profile = Profile.objects.get(user=request.user)
            message_status = 'All'
            user_profile = None
            ai_username = "compasai"
            aiprofile = Profile.objects.get(username=ai_username)
            group = None
            is_group = "False"
            is_office = False
            in_session = False

            active_path = None
            if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
                active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            
            try:
                user_profile = Profile.objects.get(username=username)
                
                ai_conversation = get_conversation(profile, user_profile)
                if user_profile == aiprofile:
                    if ai_conversation == None:
                        convo = Conversation.objects.create()
                        convo.participants.add(profile)
                        convo.participants.add(aiprofile)
                conversation = get_conversation(profile, user_profile)
                chat_messages = conversation.messages.all().order_by('timestamp')
            except:
                try:
                    group = Group.objects.get(username=username)
                except:
                    group = OfficeHour.objects.get(username=username)
                    is_office = True
      
                    # Convert the session start and end times to naive datetime objects
                    session_start_naive = datetime.strptime(f"{group.next_schedule['date']} {group.next_schedule['start_time']}", "%Y-%m-%d %H:%M:%S")
                    session_end_naive = datetime.strptime(f"{group.next_schedule['date']} {group.next_schedule['end_time']}", "%Y-%m-%d %H:%M:%S")

                    # Make the naive datetimes timezone-aware (using the current timezone)
                    session_start = timezone.make_aware(session_start_naive, timezone.get_current_timezone())
                    session_end = timezone.make_aware(session_end_naive, timezone.get_current_timezone())

                    # Get the current time (timezone-aware)
                    now = timezone.now()

                    # Check if the current time is within the session time
                    in_session = session_start <= now <= session_end
                    print(session_start)
                    print(now)
                    print(in_session)
   
                conversation = group.conversation
                chat_messages = conversation.messages.all().order_by('timestamp')
                print("done")
                is_group = "True"
               

            else:
                pass

            today = datetime.now().date()
            yesterday = today - timedelta(days=1)

            # Count unread messages
            unread_messages = 0
            first_message = 0
            for message in chat_messages:
                if message.read == False:
                    if message.sender != profile:
                        if first_message == 0:
                            first_message = message.pk
                        unread_messages += 1
            print("done tooo")
            active_path = None
            if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
                active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

            context = {
                "profile": profile,
                "messages": message_item,
                "user_profile": user_profile,
                "message_status": message_status,
                "aiprofile": aiprofile,
                "chat_messages": chat_messages,
                "today": today,
                "yesterday" : yesterday,
                "today_str": str(today),
                "yesterday_str" : str(yesterday),
                'unread_messages':unread_messages,
                "first_message": first_message,
                "is_group": is_group,
                "group": group,
                "username": username,
                "combined": combined,
                "is_office": is_office,
                "in_session": in_session,
                "conversation": conversation,
                "active_path": active_path
            }
            return render(request, 'message_detail_direct.html', context)
    except Exception as e:
        print(e)
        profile = Profile.objects.get(user=request.user)
        message_item = False
        ai_username = "compasai"
        aiprofile = Profile.objects.get(username=ai_username)
        user_profile = None

        active_path = None
        if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
            active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

        context = {
            "profile": profile,
            "messages": message_item,
            "aiprofile": aiprofile,
            "user_profile": user_profile,
            "active_path": active_path
        }
        return render(request, 'messages.html', context)

@csrf_exempt
def create_group(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')
            
            profile = Profile.objects.get(user=request.user)

            if 'image' in request.FILES:
                image =  request.FILES['image']

            if  MyProfileSkill.objects.filter(user_profile=profile).exists():
                path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            else:
                path = None
                
            event = {
                        "action": "create",
                        "user_1": profile.display_name,
                        "user_2": "",
                        "timestamp": datetime.now().isoformat()
                    }
            
            username = name.lower()
            username = username.replace(' ', '-')

            if Group.objects.filter(username=username).exists() == True:
                code = generate_code()
                print(code)
                username = username + "-" + code

            conversation = Conversation.objects.create(is_group=True)
            msg = Message.objects.create(conversation=conversation, sender=profile, text="", msg_type='', event=event)
            msg.read.add(profile)
            conversation.messages.add(msg)
            conversation.participants.add(profile)

            # Demo 
            user_1 = Profile.objects.get(username="bobniches")
            user_2 = Profile.objects.get(username="bobnichemultimedia")
            conversation.participants.add(user_1)
            conversation.participants.add(user_2)

            group = Group.objects.create(admin=profile, description=description, username=username, name=name, image=image, conversation=conversation, path=path.suggested_skill)

            return JsonResponse({'message': 'Group created successfully', 'username':username})
    
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'}, status=400)

def create_office_group(request, office_hour):
    profile = Profile.objects.get(user=request.user)
    description = ""
    name = ""
    username = office_hour['name']
    image = ""
    conversation = ""
    path = ""
    office_hour={}

    group = Group.objects.create(
        admin=profile, 
        description=description, 
        username=username, 
        name=name, 
        image=image, 
        conversation = conversation, 
        path=path, 
        is_office=True, 
        office_hour=office_hour 
    )


def get_next_weekday(start_date, target_day):
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    start_day_index = start_date.weekday()  # Get the day index of the start date
    target_day_index = days_of_week.index(target_day)  # Get the day index of the target day

    # Calculate how many days to add to reach the target day
    delta_days = (target_day_index - start_day_index) % 7
    return start_date + timedelta(days=delta_days)
# Function to convert the schedule into a string


def convert_schedule_to_string(schedule):
    def format_day_range(start_date_str, freq_weeks, target_days):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M")
        
        # Find the first occurrence of the given days
        next_occurrences = [get_next_weekday(start_date, day) for day in target_days]

        # Find the earliest of those occurrences as the actual start date
        actual_start_date = min(next_occurrences)

        # Calculate the last day of the event based on frequency
        freq_days = int(freq_weeks) * 7  # Convert weeks to days
        last_occurrences = [get_next_weekday(actual_start_date + timedelta(weeks=int(freq_weeks)-1), day) for day in target_days]
        actual_end_date = max(last_occurrences)

        # Format the date range
        start_str = actual_start_date.strftime("%b %d")
        end_str = actual_end_date.strftime("%b %d")

        return f"{start_str} to {end_str}"

    # Join days and times
    days = ' & '.join(schedule['days'])
    times = ' & '.join(schedule['time'])
    
    # Format the date range based on the schedule
    date_range = format_day_range(schedule['start'], schedule['freq'], schedule['days'])
    
    return f"Every {days} by {times} ({date_range})"


@csrf_exempt
def community(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)

    if  MyProfileSkill.objects.filter(user_profile=profile).exists():
        path = MyProfileSkill.objects.get(user_profile=profile, active=True)
    else:
        path = None

    office_groups = OfficeHour.objects.filter(path=path.suggested_skill).exclude(conversation__participants=profile).exclude(conversation__removed=profile)

    community = Community.objects.get(name=path.suggested_skill)

    groups = Group.objects.filter(path=path.suggested_skill).exclude(conversation__participants=profile).exclude(conversation__removed=profile)
    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
    context = {
        "profile": profile,
        "community": community,
        'request': request,
        "groups": groups,
        "office_groups": office_groups,
        "active_path": active_path

    }
    return render(request, 'community.html', context)

@csrf_exempt
def delete_post(request):
    try: 
        if request.method == 'POST':
            post_id = request.POST.get('id')
            post = Post.objects.get(id=post_id)
            post.delete()
            return JsonResponse({'message': 'Post created successfully'})
            
    except Exception as e:
        print(e)
       
        return JsonResponse({'error': 'Invalid request'}, status=400)

def view_post(request, slug):
    if request.user.is_authenticated == False:
        return redirect('signup')
    post = get_object_or_404(Post, slug=slug)
    profile = Profile.objects.get(user=request.user)
    print(post)
    print(slug)

    context = {
        'post': post,
        'profile': profile
        }
 
    return render(request, 'post_detail.html', context)


@csrf_exempt
def like_post(request):
    try:
        if request.method == 'POST':
            profile = Profile.objects.get(user=request.user)
            post_id = request.POST.get('id')
            post = Post.objects.get(id=post_id)

            if profile in post.likes.all():
                post.likes.remove(profile)
                count = post.likes.count()
                btn = f'''
                            <span>
                              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none">
                                <path d="M12.62 20.8116C12.28 20.9316 11.72 20.9316 11.38 20.8116C8.48 19.8216 2 15.6916 2 8.69156C2 5.60156 4.49 3.10156 7.56 3.10156C9.38 3.10156 10.99 3.98156 12 5.34156C13.01 3.98156 14.63 3.10156 16.44 3.10156C19.51 3.10156 22 5.60156 22 8.69156C22 15.6916 15.52 19.8216 12.62 20.8116Z" stroke="#9E9E54" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                              </svg>
                            </span>
                            <span>
                              {count}
                            </span>
                           '''
                return HttpResponse(btn)

            else:
                post.likes.add(profile)
                count = post.likes.count()
                btn = f'''
                            <span>
                              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none">
                                <path d="M22 8.69C22 9.88 21.81 10.98 21.48 12H2.52C2.19 10.98 2 9.88 2 8.69C2 5.6 4.49 3.1 7.56 3.1C9.37 3.1 10.99 3.98 12 5.33C13.01 3.98 14.63 3.1 16.44 3.1C19.51 3.1 22 5.6 22 8.69Z" fill="#17191D"/>
                                <path opacity="0.4" d="M21.48 12C19.9 17 15.03 19.99 12.62 20.81C12.28 20.93 11.72 20.93 11.38 20.81C8.97002 19.99 4.10002 17 2.52002 12H21.48Z" fill="#17191D"/>
                                </svg>
                            </span>
                            <span>
                              {count}
                            </span>
                          '''
                return HttpResponse(btn)
    except Exception as e:
        print(e)
        btn = f'''
                <span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M12.62 20.8116C12.28 20.9316 11.72 20.9316 11.38 20.8116C8.48 19.8216 2 15.6916 2 8.69156C2 5.60156 4.49 3.10156 7.56 3.10156C9.38 3.10156 10.99 3.98156 12 5.34156C13.01 3.98156 14.63 3.10156 16.44 3.10156C19.51 3.10156 22 5.60156 22 8.69156C22 15.6916 15.52 19.8216 12.62 20.8116Z" stroke="#9E9E54" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </span>
                
                '''
        return HttpResponse(btn)

@csrf_exempt
def comment_post(request):
    try:
        if request.method == 'POST':
            profile = Profile.objects.get(user=request.user)
            post_id = request.POST.get('id')
            comment_text = request.POST.get('text')
            print(comment_text)
            print(post_id)
            if comment_text != "":
                print(comment_text)
                post = Post.objects.get(id=post_id)

                comment = Comment.objects.create(comment_text=comment_text, comment_author=profile, comment_post=post)
                post.comments.add(comment)

            profile_data = {
                'id': profile.id,
                'display_name': profile.display_name,
                'username': profile.username,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                # Add more fields as needed
            }

            
            
            return JsonResponse({'message': 'Post created successfully', 'profile': profile_data})
            
    except Exception as e:
        print(e)
       
        return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def new_post(request):
    try:
        if request.method == 'POST':
            profile = Profile.objects.get(user=request.user)
            
            post_text = request.POST.get('text')
            comm_text = request.POST.get('community')
            images = []

            # Retrieve all images
            for key in request.FILES:
                if key.startswith('images_'):  # Assuming images are sent with keys 'images_0', 'images_1', etc.
                    uploaded_image = request.FILES[key]
                    images.append(uploaded_image)

            if post_text == "" and images == []:
                return JsonResponse({'nothing': 'Invalid request'})
            skill = Skill.objects.get(value=comm_text)
            community = Community.objects.get(name=skill)
            new_post_item = Post.objects.create(community =community, profile=profile, post_text=post_text)
            # Save each image
            for image in images:
                new_image = PostImage.objects.create(image=image)
                new_post_item.images.add(new_image)

            community.posts.add(new_post_item)

            print(new_post_item.images.all())

            return JsonResponse({'message': 'Post created successfully'})
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def course_detail(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
    
    context = {
        "profile": profile,
        "active_path": active_path
    }
    return render(request, 'course_detail.html', context)

@csrf_exempt
def project(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)

    if  MyProfileSkill.objects.filter(user_profile=profile).exists():
            path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            my_projects = Project.objects.filter(skill=path.suggested_skill, participants=profile)
            my_project_ids = my_projects.values_list('id', flat=True)  # Get a list of IDs from my_projects
            other_projects = Project.objects.exclude(id__in=my_project_ids)

    else:
            path = None
            projects = []
    

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    context = {
        "profile": profile,
        "my_projects": my_projects,
        "other_projects": other_projects,
        "active_path": active_path,
        "path": path
    }
    return render(request, 'project.html', context)

@csrf_exempt
def create_project(request):
    try:
        if request.method == 'POST':
            title = request.POST.get('title', '')
            scenario = request.POST.get('scenario', '')
            duration = request.POST.get('duration', '')
            tasks = request.POST.get('tasks', [])

            profile = Profile.objects.get(user=request.user)

            if 'image' in request.FILES:
                image =  request.FILES['image']

            if  MyProfileSkill.objects.filter(user_profile=profile).exists():
                path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            else:
                path = None

            project = Project.objects.create(duration=int(duration), skill=path.suggested_skill,title=title, scenario=scenario, tasks=tasks, image=image, owner=profile)
            project.participants.add(profile)

            return JsonResponse({'message': 'Post created successfully'})
    
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
@csrf_exempt
def update_project(request):
    try:
        if request.method == 'POST':
            id = request.POST.get('id', '')
            scenario = request.POST.get('scenario', '')
            duration = request.POST.get('duration', '')
            tasks = request.POST.get('tasks', [])

            print(scenario)
            print(duration)
            print(tasks)

            profile = Profile.objects.get(user=request.user)

            if  MyProfileSkill.objects.filter(user_profile=profile).exists():
                path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            else:
                path = None

            project_det = Project.objects.get(id=id)
            if duration:
                project_det.duration = int(duration)
            project_det.skill =path.suggested_skill
            project_det.scenario = scenario
            try:
                if 'image' in request.FILES:
                    image =  request.FILES['image']
                    project_det.image = image
            except:
                pass
            
            project_det.tasks = tasks
            project_det.owner = profile

            project_det.save()

            return JsonResponse({'message': 'Post created successfully'})
    
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'}, status=400)
    

csrf_exempt
def new_submission(request):
    try:
        if request.method == 'POST':
            profile = Profile.objects.get(user=request.user)
            post_text = request.POST.get('text')
            post_link = request.POST.get('link')
            id = request.POST.get('project')
            images = []

            # Retrieve all images
            for key in request.FILES:
                if key.startswith('images_'):  # Assuming images are sent with keys 'images_0', 'images_1', etc.
                    uploaded_image = request.FILES[key]
                    images.append(uploaded_image)

            if post_text == "" and images == []:
                return JsonResponse({'nothing': 'Invalid request'})
            
            project = Project.objects.get(id=id)

            new_sub_item = Submission.objects.create(profile=profile, post_text=post_text, project=project, post_link=post_link)
            # Save each image
            for image in images:
                new_image = PostImage.objects.create(image=image)
                new_sub_item.images.add(new_image)

            project.submissions.add(new_sub_item)
            print(new_sub_item.images.all())

            return JsonResponse({'message': 'Post created successfully'})
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'}, status=400)


csrf_exempt
def new_submission_update(request):
    print(" eqfeewfwe f")
    try:
        if request.method == 'POST':
            profile = Profile.objects.get(user=request.user)
            post_text = request.POST.get('text')
            post_link = request.POST.get('link')
            id = request.POST.get('id')
            
            images = []
           
            # Retrieve all images
            for key in request.FILES:
                if key.startswith('images_'):  # Assuming images are sent with keys 'images_0', 'images_1', etc.
                    uploaded_image = request.FILES[key]
                    images.append(uploaded_image)

            if post_text == "" and images == []:
                return JsonResponse({'nothing': 'Invalid request'})
            
            sub_item = Submission.objects.get(id=id)

            sub_item.post_text = post_text
            sub_item.post_link = post_link

            sub_item.images.clear()

            print(images)
            # Save each image
            for image in images:
                new_image, created = PostImage.objects.get_or_create(image=image)
    
                # Add the image instance to the sub_item's images field
                sub_item.images.add(new_image)
            sub_item.save()
            return JsonResponse({'message': 'Post created successfully'})
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'}, status=400)



csrf_exempt
def leavereview(request):
    try:
        if request.method == 'POST':
            profile = Profile.objects.get(user=request.user)
            rating = request.POST.get('rating')
            feedback = request.POST.get('feedback')
            id = request.POST.get('id')

            print(rating)
            print(feedback)
            print(id)

            submission = Submission.objects.get(id=id)
            review = Review.objects.create(review_text=feedback, review_rating=rating, review_author=profile, review_submission=submission)
            submission.reviews.add(review)

            profile_data = {
                'id': profile.id,
                'rating': submission.rating(),
                'reviews': submission.reviews.count(),
                'display_name': profile.display_name,
                'username': profile.username,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                # Add more fields as needed
            }

            return JsonResponse({'profile': profile_data})
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def project_detail(request, project_id):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    project = Project.objects.get(id=project_id)
    tasks = json.loads(project.tasks)
    try:
        my_submission = project.submissions.get(profile=profile)
    except:
        my_submission = None

    try:
        other_submission =  project.submissions.all()
    except:
        other_submission = None

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
    
    context = {
        "profile": profile,
        "project": project,
        "tasks": tasks,
        "my_submission": my_submission,
        "other_submissions": other_submission,
        "active_path": active_path
    }
    return render(request, 'project_detail.html', context)


@csrf_exempt
def joinproject(request, id):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        project = Project.objects.get(id=id)
        project.participants.add(profile)
        print("removedd")
    return HttpResponse('')

@csrf_exempt
def project_add(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
    
    context = {
        "profile": profile,
        "active_path": active_path
    }
    return render(request, 'project_add_overlay.html', context)

@csrf_exempt
def project_edit(request, project_id):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    project = Project.objects.get(id=project_id)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)

    context = {
        "profile": profile,
        "active_path": active_path
    }
    return render(request, 'project_edit_overlay.html', context)
    

def get_roadmap_duration(roadmap_data):
    
    roadmap_duration = 0
    for level in roadmap_data:
        for section in level['sections']:
            roadmap_duration += int(section.get('duration', 0))

    return roadmap_duration

@csrf_exempt
def roadmap_detail(request, id):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)
    try:
        path = MyProfileSkill.objects.get(user_profile=profile, active=True)
    except:
        path = None
    roadmap_data = path.roadmap
    
    item = None
    for level in roadmap_data:
        # Loop through each section within the level
        for section in level['sections']:
            # Check if the section's id matches the given section_id
            if section.get('id') == id:
                item = section

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)
   
    context = {
        "profile": profile,
        "roadmap": roadmap_data,
        "item": item,
        "path": path,
        "active_path": active_path

    }
    return render(request, 'roadmap_detail.html', context)


@csrf_exempt
def roadmap(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    profile = Profile.objects.get(user=request.user)

    try:
        path = MyProfileSkill.objects.get(user_profile=profile, active=True)
    except:
        path = None
    roadmap_data = path.roadmap
    roadmap_duration = get_roadmap_duration(roadmap_data)
    
    start_date = roadmap_data[0]['startdate']
    print(start_date)
    roadmap_weeks = get_weeks_dates(roadmap_duration, start_date)

    active_path = None
    if  MyProfileSkill.objects.filter(user_profile=profile, active=True).exists():
        active_path = MyProfileSkill.objects.get(user_profile=profile, active=True)  

    context = {
        "profile": profile,
        "roadmap_weeks": roadmap_weeks,
        "active_path": active_path,
        "roadmap": roadmap_data
    }
    return render(request, 'roadmap.html', context)

@csrf_exempt
def mark_task(request):
    try:
        if request.method == 'POST':
            profile = Profile.objects.get(user=request.user)
            task_id = int(request.POST.get('task_id'))
            item_id = int(request.POST.get('item_id'))
            try:
                path = MyProfileSkill.objects.get(user_profile=profile, active=True)
            except:
                path = None
            roadmap_data = path.roadmap

            for level_index, level in enumerate(roadmap_data):
                for i, section in enumerate(level['sections']):
                    if section['id'] == item_id:
                        item = section
                        total_tasks = len(item['tasks'])
                        completed_tasks = 0

                        # Mark the task as done
                        for task in item['tasks']:
                            if task['sub_id'] == task_id:
                                task['status'] = "done"
                                print(f"Task '{task['name']}' is now marked as done.")
                            
                            # Count how many tasks are done
                            if task['status'] == "done":
                                completed_tasks += 1

                        # Calculate progress
                        progress_percentage = (completed_tasks / total_tasks) * 100
                        item['progress'] = progress_percentage  # Update section progress
                        print(f"Progress for section '{item['title']}' updated to {progress_percentage}%")

                        # If current section progress is 100%
                        if progress_percentage == 100:
                            # Check if there's a next section in the same level
                            if i + 1 < len(level['sections']):
                                next_section = level['sections'][i + 1]
                                if next_section['progress'] == 0:  # If the next section's progress is still 0
                                    next_section['progress'] = 5
                                    print(f"Progress for next section '{next_section['title']}' set to 5%.")
                            # If this is the last section in the current level, move to the next level
                            elif level_index + 1 < len(roadmap_data):
                                next_level = roadmap_data[level_index + 1]
                                if next_level['sections'][0]['progress'] == 0:  # If the first section of the next level is not started
                                    next_level['sections'][0]['progress'] = 5
                                    print(f"Progress for the first section of next level '{next_level['sections'][0]['title']}' set to 5%.")

            # Update the profile roadmap
            path.roadmap = roadmap_data
            path.save()

            return JsonResponse({'message': 'Task done successfully, progress updated, and next section/level started'})

    except Exception as e:
        print(e)
        return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def task_progress(request):
    percentage = 60  # Example percentage, replace with actual logic to get progress
    angle = percentage * 3.6

    # Create the CSS for the progress circle dynamically
    css = f'''
    <style>
        .home_section-chat-roadmap-item-tasks-item.active .home_section-chat-roadmap-item-tasks-item-info-progress-circle::before {{
            transform: rotate({angle if percentage <= 50 else 180}deg);
        }}
       .home_section-chat-roadmap-item-tasks-item.active  .home_section-chat-roadmap-item-tasks-item-info-progress-circle::after {{
            transform: rotate({0 if percentage <= 50 else angle - 180}deg);
        }}
    </style>
    '''

    # Respond with the CSS and the inner content of the progress circle
    response = f'{css}<div class="home_section-chat-roadmap-item-tasks-item-info-progress-circle-overlay"></div>'
    return HttpResponse(response)

def send_activation_email(request, user, receiver):
    current_site = get_current_site(request)
    profile = Profile.objects.get(user=user)
    subject = 'Activate your Compas AI account.'
            
    domain = current_site.domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    activate_code = f"http://{domain}/activate/{uid}/{token}"
    print(activate_code)

    # Render the email message HTML template
    message_html = render_to_string('email_confirmation.html', {'profile': profile, 'activate_url': activate_code})

    # Create a multipart message and set the content type to text/html
    msg = MIMEMultipart()
    sender_name = 'Compas AI'
    msg['From'] = f'{sender_name} <{env("EMAIL_HOST_USER")}>'
    msg['To'] = receiver  # Set the recipient email address
    msg['Subject'] = subject

    # Attach the HTML message to the email
    msg.attach(MIMEText(message_html, 'html'))

    # Send the email
    smtpserver = smtplib.SMTP_SSL('mail.privateemail.com', 465)
    smtpserver.ehlo()
    smtpserver.login(env('EMAIL_HOST_USER'), env('EMAIL_HOST_PASSWORD'))
    smtpserver.sendmail(msg['From'], msg['To'], msg.as_string())
    smtpserver.quit()

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        profile = Profile.objects.get(user=user)
        print(profile)
        profile.is_confirmed = True
        print("profile has been updated")
        profile.save()
        send_welcome_email(request,user, profile.email)
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        # Redirect to the URL with anchor
    
        return redirect('signup')
    else:
        return HttpResponse('Activation link is invalid!')


def send_welcome_email(request, user, receiver):
    current_site = get_current_site(request)
    profile = Profile.objects.get(user=user)
    subject = 'Welcome to Compas AI.'
            
    domain = current_site.domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    home_url = f"https://{domain}/"

    # Render the email message HTML template
    message_html = render_to_string('welcome_email.html', {'profile': profile, 'home_url': home_url})

    # Create a multipart message and set the content type to text/html
    msg = MIMEMultipart()
    sender_name = 'Compas AI'
    msg['From'] = f'{sender_name} <{env("EMAIL_HOST_USER")}>'
    msg['To'] = receiver  # Set the recipient email address
    msg['Subject'] = subject

    # Attach the HTML message to the email
    msg.attach(MIMEText(message_html, 'html'))

    # Send the email
    smtpserver = smtplib.SMTP_SSL('mail.privateemail.com', 465)
    smtpserver.ehlo()
    smtpserver.login(env('EMAIL_HOST_USER'), env('EMAIL_HOST_PASSWORD'))
    smtpserver.sendmail(msg['From'], msg['To'], msg.as_string())
    smtpserver.quit()


def send_referral_reward_email(request, user, receiver, referred_name, referred_email):
    current_site = get_current_site(request)
    profile = Profile.objects.get(user=user)
    subject = 'You have a reward!.'
            
    domain = current_site.domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    home_url = f"https://{domain}/"

    # Render the email message HTML template
    message_html = render_to_string('referral_email.html', {'profile': profile, 'home_url': home_url, 'user_name': referred_name, 'user_email': referred_email})

    # Create a multipart message and set the content type to text/html
    msg = MIMEMultipart()
    sender_name = 'Compas AI'
    msg['From'] = f'{sender_name} <{env("EMAIL_HOST_USER")}>'
    msg['To'] = receiver  # Set the recipient email address
    msg['Subject'] = subject

    # Attach the HTML message to the email
    msg.attach(MIMEText(message_html, 'html'))

    # Send the email
    smtpserver = smtplib.SMTP_SSL('mail.privateemail.com', 465)
    smtpserver.ehlo()
    smtpserver.login(env('EMAIL_HOST_USER'), env('EMAIL_HOST_PASSWORD'))
    smtpserver.sendmail(msg['From'], msg['To'], msg.as_string())
    smtpserver.quit()



@csrf_exempt
def error_404(request, exception):
    return render(request, '404.html', status=404)

@csrf_exempt
def error_500(request):
    return render(request, '404.html', status=500)

@csrf_exempt
def terms_and_conditions(request):
    return render(request, 'terms_and_condition.html')

@csrf_exempt
def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def get_adjacent_stage(current_stage, action):
    # Find the index of the current stage
    current_index = next((index for (index, d) in enumerate(stages) if d["stage"] == current_stage), None)
    
    if current_index is None:
        return None  # If the current stage is not found

    if action == "NEXT":
        if current_index < len(stages) - 1:
            return stages[current_index + 1]
        else:
            return None  # Already at the last stage
    elif action == "PREVIOUS":
        if (current_index == 1):
            return stages[current_index]
        elif current_index > 1:
            return stages[current_index - 1]
        else:
            return None  # Already at the first stage
    else:
        return None  # Invalid action


def get_stage_percent(current_stage):
    # Find the index of the current stage
    current_index = next((index for (index, d) in enumerate(stages) if d["stage"] == current_stage), None)
    return ((current_index+1)/len(stages))*100
    

def get_stage_dict(stage_name):
    
    for stage in stages:
        if stage["stage"] == stage_name:
            return stage
    return None

def get_weeks_dates(num_weeks, start_date):
    weeks_dates = {}

    start_date = datetime.strptime(start_date, "%Y-%m-%d")

    for week in range(1, num_weeks + 1):
        end_date = start_date + timedelta(days=6)  # Calculate the end date of the week

        # Format the dates to a readable format (e.g., "Jan 1")
        start_date_str = start_date.strftime("%b %d")
        end_date_str = end_date.strftime("%b %d")

        # Add to dictionary
        weeks_dates[f"{week}"] = f"{start_date_str} - {end_date_str}"

        # Move to the next week
        start_date = end_date + timedelta(days=1)

    return weeks_dates

fields = ["Graphics Design","Web Design","Motion Graphics","Animation","Video Editing","Content Writing","Content Creation","Product Design","Product Management","Scrum Management","Product Marketing","Business Analysis","Business Intelligence","Business Analytics","Business Development","Financial Analysis","Legal and Compliance","Customer Relationship Management (CRM)","Digital Marketing","Content Marketing","Public Relations (PR)","Community Management","Game Development","Mobile App Development","Database Management","Frontend Development","Backend Development","Fullstack Development","Blockchain Development","Trading Algorithm Development","Quality Assurance","Cloud & DevOps","Cybersecurity","Data Analysis","Data Analytics","Data Science","Data Engineering","Artificial Intelligence","Project Management","IT Administration","Customer Support","Virtual Assistant"]
resources = ["Mobile Phone","Laptop","Desktop","Tablet","Ipad"]

stages = [
        {
            "stage": "WELCOME",
            "comment": "",
            "question": "",
            "tip": "",
            "placeholder": "",

        },
        {
            "stage": "CONTACT",
            "comment": "Let's get you started",
            "question": "Please share your contact information.",
            "tip": "",
            "placeholder": "Your full name",
        },

        {
            "stage": "DESCRIPTION",
            "comment": "Let's get you started",
            "question": "Which best describes you?",
            "tip": "",
            "placeholder": "",
        },
        
        {
            "stage": "STATUS",
            "comment": "",
            "question": "Have you started learning a tech skill?",
            "tip": "If yes, select max of 3 skills else leave blank",
            "placeholder": "Select skills",

        },
        {
            "stage": "HOURS",
            "comment": "",
            "question": "How many hours a week?",
            "tip": "Weekly availability to learn and practice",
            "placeholder": "Select hours from 1 to 40",

        },
        {
            "stage": "RESOURCES",
            "comment": "",
            "question": "Which of these resources can you have access to?",
            "tip": "Select as many as possible",
            "placeholder": "",
        
        },
        {
            "stage": "COMPUTERS",
            "comment": "",
            "question": "How proficient are you with computers?",
            "tip": "Slide to level",
            "placeholder": "",

        },
        {
            "stage": "STRENGTHS",
            "comment": "",
            "question": "What are your strengths?",
            "tip": "Select your top 5 strengths",
            "placeholder": "",

        },
        {
            "stage": "WEAKNESS",
            "comment": "",
            "question": "What are your weaknesses?",
            "tip": "Select your top 5 weaknesses",
            "placeholder": "",

        },
        {
            "stage": "TEAM",
            "comment": "",
            "question": "Do you prefer working in a team or alone?",
            "tip": "",
            "placeholder": "",
        },
        {
            "stage": "INTERESTS",
            "comment": "",
            "question": "Tell me about how you spend your free time.",
            "tip": "Hobbies, Routines, habits e.t.c",
            "placeholder": "Briefly in abour 200 words",

        },
        {
            "stage": "ACADEMICS",
            "comment": "",
            "question": "Tell me about your academic background.",
            "tip": "Field of study, level of study, inspiration, favorite subjects, grades e.t.c.",
            "placeholder": "Briefly in abour 200 words",

        },
        {
            "stage": "EXPOSURE",
            "comment": "",
            "question": "Do you have any prior exposure to technology?",
            "tip": "Any experience with technology-related projects or activities outside of your academic studies?",
            "placeholder": "Briefly in abour 200 words",

        },
        {
            "stage": "MOTIVATION",
            "comment": "",
            "question": "⁠What is your motivation to acquire a tech skill?",
            "tip": "Why tech 🤷🏻‍♂️?",
            "placeholder": "Briefly in abour 200 words",

        },
        {
            "stage": "THANKYOU",
            "comment": "",
            "question": "Thank you for answering my questions accordingly!",
            "tip": "Please hold as I help recommend a learning path for you",
            "placeholder": "",
        }

        ]

soft_skills = ["Communication","Teamwork","Problem-Solving","Adaptability","Critical Thinking","Creativity","Time Management","Attention to Detail","Leadership","Collaboration","Emotional Intelligence","Conflict Resolution","Decision Making","Organizational Skills","Interpersonal Skills","Negotiation","Project Management","Analytical Thinking","Innovation","Stress Management","Presentation Skills"
]


def add_skill():
    skills = [
            {"category": "Creative", "skills": "Graphics Design"},
            {"category": "Creative", "skills": "Web Design"},
            {"category": "Creative", "skills": "Motion Graphics"},
            {"category": "Creative", "skills": "Animation"},
            {"category": "Creative", "skills": "Video Editing"},
            {"category": "Creative", "skills": "Content Writing"},
            {"category": "Creative", "skills": "Content Creation"},
            {"category": "Product", "skills": "Product Design"},
            {"category": "Product", "skills": "Product Management"},
            {"category": "Product", "skills": "Scrum Management"},
            {"category": "Product", "skills": "Product Marketing"},
            {"category": "Business", "skills": "Business Analysis"},
            {"category": "Business", "skills": "Business Intelligence"},
            {"category": "Business", "skills": "Business Analytics"},
            {"category": "Business", "skills": "Business Development"},
            {"category": "Business", "skills": "Financial Analysis"},
            {"category": "Business", "skills": "Legal and Compliance"},
            {"category": "Business", "skills": "Customer Relationship Management (CRM)"},
            {"category": "Marketing", "skills": "Digital Marketing"},
            {"category": "Marketing", "skills": "Content Marketing"},
            {"category": "Marketing", "skills": "Public Relations (PR)"},
            {"category": "Marketing", "skills": "Community Management"},
            {"category": "Engineering", "skills": "Game Development"},
            {"category": "Engineering", "skills": "Mobile App Development"},
            {"category": "Engineering", "skills": "Database Management"},
            {"category": "Engineering", "skills": "Frontend Development"},
            {"category": "Engineering", "skills": "Backend Development"},
            {"category": "Engineering", "skills": "Fullstack Development"},
            {"category": "Engineering", "skills": "Blockchain Development"},
            {"category": "Engineering", "skills": "Trading Algorithm Development"},
            {"category": "Engineering", "skills": "Quality Assurance"},
            {"category": "Engineering", "skills": "Cloud & DevOps"},
            {"category": "Engineering", "skills": "Cybersecurity"},
            {"category": "Data", "skills": "Data Analysis"},
            {"category": "Data", "skills": "Data Analytics"},
            {"category": "Data", "skills": "Data Science"},
            {"category": "Data", "skills": "Data Engineering"},
            {"category": "Data", "skills": "Artificial Intelligence"},
            {"category": "Operations", "skills": "Project Management"},
            {"category": "Operations", "skills": "IT Administration"},
            {"category": "Operations", "skills": "Customer Support"},
            {"category": "Operations", "skills": "Virtual Assistant"}
        ]

    for skill in skills:
        skill_new = Skill.objects.create(name=skill['skills'],category=skill['category'])
        skill_new.save()

def generate_code():
        # Generate a random code of maximum length 6
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def add_community():
    skills = Skill.objects.all()
    for skill in skills:
        Community.objects.get_or_create(name=skill)
        print("djsj")

#add_community()

def update_skills():
    skills = Skill.objects.all()

    for skill in skills:
        skill_url = skill.name.lower()
        skill_url = skill_url.replace(' ', '-')
        skill.value = skill_url
        skill_url = skill_url + '.svg'
        skill.icon = skill_url
        skill.save()
        print(skill.icon)