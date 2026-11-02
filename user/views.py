import requests
import json
import time

from django.shortcuts import render
from django.http import HttpResponseRedirect
import requests
from .forms import UserRegisterForm,UserLoginForm,UserProfile,ChangePassword
from django.contrib import messages
from django.shortcuts import redirect
from django.core.paginator import Paginator

# Create your views here.

def redirect_page(request):

    form = UserLoginForm()
    messages.success(request,"Your password is successfully reset. Continue to login with new password.")
    return render(request,'user/redirect.html')
    
    
def landing(request):

    response = render(request,'user/landing.html')
    
    response.delete_cookie("user_profile")
    response.delete_cookie("user_registered")
    response.delete_cookie("user_mail")
    response.delete_cookie("user_token")
    response.delete_cookie('profile_changed')
    response.delete_cookie('user_jobs_list_exist')
    return response

def user_reg(request):
    
    if request.method=="GET":
        form = UserRegisterForm()
        return render(request,'user/sign.html',{'form':form})
    else:
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            email = request.POST.get('email')            
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            register = requests.post("https://singularjobapi.herokuapp.com/user_account/register/", data={'email':email,'username':username,'password':password,'confirm_password':confirm_password})
            api_messages = json.loads(register.text)
            print(api_messages)
            if api_messages['api_status']=="200":                
                messages.success(request,'You are successfully registered.')
                messages.info(request,'An account activation mail is sent to your registered email. Click on the link to activate your account.')
                return render(request,'user/sign.html')
            else:
                for errors in api_messages['message']:
                    messages.info(request,errors)
                #return render(request,'user/sign.html',{'form':form})
                return HttpResponseRedirect('https://singularjobs.herokuapp.com/singular-jobs/register')
            
        else:
            for field in form.non_field_errors():
                messages.error(request,field)
            forms = UserRegisterForm()
            #return render(request,'user/sign.html',{'form':forms})
            return HttpResponseRedirect('https://singularjobs.herokuapp.com/singular-jobs/register')
    

def user_login(request):


    if request.method=="GET":
        '''
        system_messages = messages.get_messages(request)
        for message in system_messages:
            # This iteration is necessary
            pass
        '''
        form = UserLoginForm()
        return render(request,'user/login.html',{'form':form})

    else:
        form = UserLoginForm(request.POST)
        if form.is_valid():
                        
            email = request.POST.get('email')            
            password = request.POST.get('password')
            login = requests.post("https://singularjobapi.herokuapp.com/user_account/login/", data={'username':email,'password':password})
            api_messages = json.loads(login.text)
            
            print(api_messages)
            if api_messages['api_status']=="200":   
                messages.success(request,'You are successfully authenticated. Now being redirected to Profile Page.')
                html = render(request,'user/login_redirect.html')
                html.delete_cookie('user_profile')
                html.delete_cookie('user_registered')
                html.delete_cookie('profile_changed')
                html.delete_cookie('user_jobs_list_exist')
                html.set_cookie('user_token',api_messages['token'])
                html.set_cookie('user_mail',api_messages['email'])
                html.set_cookie('username',api_messages['username'])
                 
                return html
            elif api_messages['api_status']=="404":
                messages.error(request,api_messages['message'][0])    
                return HttpResponseRedirect('https://singularjobs.herokuapp.com/singular-jobs/login')
            else:
                messages.error(request,api_messages['message'][0])    
                #return render(request,'user/login.html',{'form':form})
                return HttpResponseRedirect('https://singularjobs.herokuapp.com/singular-jobs/login')
        else:
            for field in form.non_field_errors():
                messages.error(request,field)  
            time.sleep(2)
            #return HttpResponseRedirect('http://localhost:8000/register/login')
            #return render(request,'user/login.html',{'form':form})
            return HttpResponseRedirect('https://singularjobs.herokuapp.com/singular-jobs/login')
        
def user_profile(request):
    
   
    if request.method=="GET":
        print(request.COOKIES)
        if 'user_token' not in request.COOKIES.keys():
            form = UserLoginForm()
            return HttpResponseRedirect('https://singularjobs.herokuapp.com/singular-jobs/login')
    
        form = UserProfile()
        
        if 'user_profile' not in request.COOKIES.keys():
        
            data = requests.post('https://singularjobapi.herokuapp.com/user_account/check/',data={'email':request.COOKIES['user_mail']})
            user_data = json.loads(data.text)
            print(user_data)  
            
            html = render(request,'user/profile.html',{'form':form,'profile':user_data['user_profile'],'username':request.COOKIES['username']})
            
            if user_data['user_status']=="200":
                user_registered=True
                html.set_cookie('user_profile',user_data['user_profile'])
                html.set_cookie('user_jobs_list_exist',user_data['user_profile']['user_jobs_list_exist'])
            else:
                user_registered=False
                
            html.set_cookie('user_registered',user_registered)
            return html
        else:
            #'user_profile':request.COOKIES['user_profile'] pass this into form when needed.
            print(request.COOKIES)
            user_profile = eval(request.COOKIES['user_profile'])
            return render(request,'user/profile.html',{'form':form,'profile':user_profile,'username':request.COOKIES['username']})
    
    
    else:
    
        form = UserProfile(request.POST)
        
        if form.is_valid():
            print(type(request.COOKIES['user_registered']))
            print(request.COOKIES['user_registered'])
            
            from .entity_matching import EntityMatch
            
            # create user profile.
            if request.COOKIES['user_registered']=="False":
                form_errors=[]
                if request.POST.get('technical_skills')=="":
                    form_errors.append("Technical skills required.")
                #if request.POST.get('linkedin_profile')=="https://linkedin.com/abc":
                #    form_errors.append("Linkedin Profile required.")
                if form_errors!=[]:
                    return render(request,'user/profile.html',{'form':form,'form_errors':form_errors,'username':request.COOKIES['username']})
                
                data = {}
                
                #data['technical_skills'] = request.POST.get('technical_skills')
                data['soft_skills'] = request.POST.get('soft_skills').lower()
                data['job_types'] = request.POST.get('job_types').lower()
                data['subject_interest'] = request.POST.get('subject_interest').lower()
                data['linkedin_profile'] = request.POST.get('linkedin_profile')
                data['email'] = request.COOKIES['user_mail']
                
                entities = EntityMatch()
                tech_skills = request.POST.get('technical_skills').lower()
                data['technical_skills'] = entities.entities_multithread(tech_skills.split(","))
                del entities
                
                profile = requests.post("https://singularjobapi.herokuapp.com/user_account/create/",headers={'Authorization':f"Token {request.COOKIES['user_token']}"},data=data)
                api_messages = json.loads(profile.text)
                print(api_messages)
                
                if api_messages['api_status']=="200":                
                    messages.success(request,'Your profile is successfully created.')            
                    html = render(request,'user/profile.html',{'form':form,'username':request.COOKIES['username']})
                    html.set_cookie('user_registered',True)
                    html.set_cookie('user_profile',data)
                    html.set_cookie('profile_changed',True)
                    html.set_cookie('user_jobs_list_exist',False)
                    return html
                    
                else:
                    messages.error(request,'Some error occured. Kindly again submit your profile.')
                    html = render(request,'user/profile.html',{'form':form,'username':request.COOKIES['username']})
                    return html
            
            else:
                update_data = {}
                
                user_profile = eval(request.COOKIES['user_profile'])
                
                if request.POST.get('technical_skills')!=user_profile['technical_skills']:
                    entities = EntityMatch()
                    update_tech_skills = request.POST.get('technical_skills').lower()
                    update_data['technical_skills']=entities.entities_multithread(update_tech_skills.split(","))
                    del entities
                if request.POST.get('soft_skills')!=user_profile['soft_skills']:
                    update_data['soft_skills']=request.POST.get('soft_skills')
                if request.POST.get('job_types')!=user_profile['job_types']:
                    update_data['job_types']=request.POST.get('job_types')
                if request.POST.get('subject_interest')!=user_profile['subject_interest']:
                    update_data['subject_interest']=request.POST.get('subject_interest')
                if request.POST.get('linkedin_profile')!=user_profile['linkedin_profile']:
                    update_data['linkedin_profile']=request.POST.get('linkedin_profile')
                
                
                if update_data == {}:
                    messages.info(request,"No data to update.")
                    return render(request,'user/profile.html',{'form':form,'profile':user_profile,'username':request.COOKIES['username']})
                else:
                    update_data['email'] = request.COOKIES['user_mail']                    
                    update = requests.patch('https://singularjobapi.herokuapp.com/user_account/update/',headers={'Authorization':f"Token {request.COOKIES['user_token']}"},data=update_data)
                    api_messages = json.loads(update.text)
                    print(api_messages)
                    if api_messages['status']=="200":                
                        messages.success(request,'Your profile is successfully updated.')            
                        
                        updated_data = {}
                        updated_data['technical_skills'] = update_data.get('technical_skills',user_profile['technical_skills'])
                        updated_data['soft_skills'] = update_data.get('soft_skills',user_profile['soft_skills'])
                        updated_data['job_types'] = update_data.get('job_types',user_profile['job_types'])
                        updated_data['subject_interest'] = update_data.get('subject_interest',user_profile['subject_interest'])
                        updated_data['linkedin_profile'] = update_data.get('linkedin_profile',user_profile['linkedin_profile'])
                        
                        html = render(request,'user/profile.html',{'form':form,'profile':updated_data,'username':request.COOKIES['username']})
                        html.set_cookie('profile_changed',True)
                        html.set_cookie('user_profile',updated_data)
                        return html
                    else:
                        #if data not updated retrun errors occured.
                        messages.error(request,'Some error occured while updating your profile. Kindly resubmit.')
                        return render(request,'user/profile.html',{'form':form,'username':request.COOKIES['username']})
                        
        else:
            for field in form.non_field_errors():
                messages.error(request,field)
            return render(request,'user/profile.html',{'form':form,'username':request.COOKIES['username']})
    

# NOT COMPLETE.
def my_jobs(request):

    # call neo4j
    '''
    if 'user_profile_created' in request.COOKIES.keys():        
        user_jobs = requests.post('http://127.0.0.1:8000/api/user_account/myjobs/',headers={'Authorization':f"Token {request.COOKIES['user_token']}"},data={'email':request.COOKIES['user_mail'],'user_profile_created':request.COOKIES['user_profile_created']})        
    else:
        user_jobs = requests.post('http://127.0.0.1:8000/api/user_account/myjobs/',headers={'Authorization':f"Token {request.COOKIES['user_token']}"},data={'email':request.COOKIES['user_mail'],'user_profile_created':False})
        
    '''
    if 'user_jobs_list_exist' not in request.COOKIES.keys():
        user_jobs_list_exist="False"
    else:
        user_jobs_list_exist = request.COOKIES['user_jobs_list_exist']
    jobs_response = requests.post('https://singularjobapi.herokuapp.com/user_account/myjobs/',headers={'Authorization':f"Token {request.COOKIES['user_token']}"},data={'email':request.COOKIES['user_mail'],'user_jobs_list_exist':user_jobs_list_exist})
    
    # user_jobs is a list of dictionaries.
    # do pagination
    user_jobs = json.loads(jobs_response.text)
    print(user_jobs)
    jobs_paginator = Paginator(user_jobs['recommend_jobs'][0]['jobs'],10)
    page_num = request.GET.get('page',1)
    #page_num=1
    try:
        page = jobs_paginator.page(page_num)
    except:
        page = jobs_paginator.page(page_num)
    
    print(page)
    
    context = {'jobs':page,'username':request.COOKIES['username']}
    html = render(request,'user/myjobs.html',context)
    html.set_cookie('user_jobs_list_exist',True)
    return html
      
    
def delete_cookies(response):

    print(12345789)
    response.delete_cookie("user_profile")
    response.delete_cookie("user_registered")
    #response.delete_cookie("profile_changed")
    response.delete_cookie("user_mail")
    response.delete_cookie("user_token")
    
    return response

def logout(request):
    
    print(request.COOKIES)
    token = request.COOKIES['user_token']
    print("........................................             ", token)
    #logout_message = requests.post("http://localhost:8000/api/user_account/logout/",headers={'Authorization':f"Token {request.COOKIES['user_token']}"})
    messages.success(request,"You are successfully logged out.")
    response = HttpResponseRedirect("https://singularjobs.herokuapp.com/singular-jobs/login")
    response.delete_cookie("user_profile")
    response.delete_cookie("user_registered")
    response.delete_cookie("user_mail")
    response.delete_cookie("user_token")
    response.delete_cookie("user_jobs_list_exist")
    response.delete_cookie("username")
    #response = delete_cookies(response)
    
    return response


def change_password(request):

    if request.method=="GET":
        form = ChangePassword()
        return render(request,'user/change_password.html',{'form':form})
    else:
        form = ChangePassword(request.POST)
        if form.is_valid():
            change_password = requests.patch('https://singularjobapi.herokuapp.com/user_account/change_password/',data={'new_password':request.POST.get('new_password'),'email':request.POST.get('email')})
            api_messages = json.loads(change_password.text)
            print(api_messages)
            if api_messages['status']=="201":
                messages.info(request,"An email is sent to your registered email. Click on the link to change your password.")
                #login_form = UserLoginForm()
                #return redirect('login')
                return render(request,'user/change_password.html',{'form':form})
            elif api_messages['status']=="404":
                messages.error(request,"You have not verified your account yet. Kindly verify your account first.")
                return render(request,'user/change_password.html',{'form':form})
            else:
                messages.error(request,"Some error occured. Please try again. May be your account is not verified.")
                return render(request,'user/change_password.html',{'form':form})
        
        for field in form.non_field_errors():
                messages.error(request,field)                
        return render(request,'user/change_password.html',{'form':form})
        
        
def faq(request):

    if request.method=="GET":
    
        return render(request,'user/faq.html');
        
        
