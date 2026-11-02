from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
import re


def email_validation(email):

    if re.match(r'.*@gmail\.com',email)==None:
        return False
    return True
    
def username_validation(username):

    if re.match(r'(.*_.*|^[a-zA-Z0-9]+$)',username)==None:
        return False
    return True
    
def password_similarity(password,confirm_password):
    
    if password!=confirm_password:
        return False
    return True

def password_length(password):
    
    if len(password)<8:
        return False
    return True
    
def password_chars(password):

    if '#' in password or '$' in password:
        return False
    return True

def linkedin_validation(linkedin_url):

    if re.match(r'^(^(https:\/\/www\.linkedin\.com\/.*))',linkedin_url):
        print(linkedin_url)
        return True
    return False


class UserRegisterForm(forms.Form):

    username = forms.CharField(label='username')
    email = forms.EmailField(label='email')
    password = forms.CharField(label='password',widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='confirm_password',widget=forms.PasswordInput())
    
    def clean(self):
               
        super(UserRegisterForm,self).clean()    
        errors = []
        
        email=self.cleaned_data['email']
        username=self.cleaned_data['username']
        password=self.cleaned_data['password']
        confirm_password=self.cleaned_data['confirm_password']
        
        if email_validation(email)==False:
            errors.append(ValidationError('Invalid Email.It should be of form : abc@gmail.com'))
        if username_validation(username)==False:
            errors.append(ValidationError('Invalid Username.It should be of form : abc_xyz'))
        if password_similarity(password,confirm_password)==False:
            errors.append(ValidationError('Passwords did not match. Kindly check your password.'))
        if password_length(password)==False:
            errors.append(ValidationError('Password length should be atleast 8 characters long.'))
        if password_chars(password)==False:
            errors.append(ValidationError('Password should not contain $ or #'))
        
        print(errors)
        if errors:
            raise ValidationError(errors)


class UserLoginForm(forms.Form):

    email = forms.EmailField(label='email')
    password = forms.CharField(label='password',widget=forms.PasswordInput())
    
    def clean(self):
               
        super(UserLoginForm,self).clean()    
        errors = []
        
        email=self.cleaned_data['email']
        password=self.cleaned_data['password']
        
        if email_validation(email)==False:
            errors.append(ValidationError('Invalid Email.It should be of form : abc@xyz.com'))
        if password_length(password)==False:
            errors.append(ValidationError('Password length should be atleast 8 characters long.'))
        if password_chars(password)==False:
            errors.append(ValidationError('Password should not contain $ or #'))
            
        if errors:
            raise ValidationError(errors)
            
            
class UserProfile(forms.Form):

    technical_skills = forms.CharField(label='technical_skills',initial="")
    soft_skills = forms.CharField(label='soft_skills',required=False,initial="")
    job_types = forms.CharField(label='job_types',required=False,initial="")
    subject_interest = forms.CharField(label='subject_interest',required=False,initial="")
    linkedin_profile = forms.URLField(label='linkedin_profile',required=False,initial="")
    print(linkedin_profile)

    def clean(self):
        super(UserProfile,self).clean()    
        errors = []   
        linkedin_url = self.cleaned_data['linkedin_profile']
        if linkedin_validation(linkedin_url)==False:
            errors.append(ValidationError('Enter proper url profile. It should be of form https://www.linkedin.com/'))

        if errors:
            raise ValidationError(errors)
            

class ChangePassword(forms.Form):

    
    email = forms.EmailField(label='email') 
    new_password = forms.CharField(label='new_password',widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='confirm_password',widget=forms.PasswordInput())
    
    def clean(self):
        super(ChangePassword,self).clean()    
        errors = []
        
        email=self.cleaned_data['email']
        new_password=self.cleaned_data['new_password']
        confirm_password=self.cleaned_data['confirm_password']
        
        if email_validation(email)==False:
            errors.append(ValidationError('Invalid Email.It should be of form : abc@xyz.com'))
        if password_similarity(new_password,confirm_password)==False:
            errors.append(ValidationError('Passwords did not match. Kindly check your password.'))
        if password_length(new_password)==False:
            errors.append(ValidationError('Password length should be atleast 8 characters long.'))
        if password_chars(new_password)==False:
            errors.append(ValidationError('Password should not contain $ or #'))
            
        if errors:
            raise ValidationError(errors)
