from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.decorators import login_required
# Create your views here.
import pyotp
import plivo
import datetime
from basicapp import models,forms
from basicapp.shortener_algo import algo
from django.http import HttpResponseRedirect,HttpResponse
from django.utils import timezone

from urllib.parse import urlparse

BASE_URL='http://127.0.0.1:8000/'



def send_otp(phoneno, new_otp):
    '''
    Modify this function to set new sms service
    '''
    client = plivo.RestClient(auth_id='MAMZVKZGY4MWRJNJRMYW', 
                        auth_token='M2ZkZjI0YTE2YTFkNzNhZWU0MjU1YjE4ZGMwNDM3')
    client1 = client
    try:
        response = client1.messages.create(
                    src='+919503182221',
                    dst='91'+str(phoneno),
                    text='Hi this is the OTP: '+str(new_otp),
                )
        print(response.__dict__)
        return 'Message sent'
    except plivo.exceptions.PlivoRestError as e:
        print(e)
        return 'Message not sent'


def generate_and_save_otp(phoneno):
    totp = pyotp.TOTP('base32secret3232')
    new_otp = totp.now()
    send_otp(phoneno,new_otp)
    try:
        user = models.User.objects.get(phone_no = phoneno)
        user.set_password(new_otp)
        user.save()
    except:
        user = models.User.objects.create_user(phone_no = phoneno, password=new_otp)
        user.save()
    return

def auth(request):
    phoneno = request.POST.get('phone_no')
    if request.method=='POST':
        generate_and_save_otp(phoneno)
        return render(request,'verify.html',{'phone_no':phoneno})
    else:
        return render(request,'auth.html',{'phone_no':None})
    
def verify(request):
    phoneno = request.POST.get('phone_no')
    otp = request.POST.get('get_otp')
    if request.method=='POST':
        user = authenticate(request, username=phoneno, password=otp)
        if user is not None:
            login(request, user)
            return redirect('shorten')
        else:
            return render(request,'verify.html',{'phone_no':phoneno, 'message':'Invalid OTP'})
    else:
        return redirect('auth')
    
def logout_user(request):
    logout(request)
    return redirect('auth')


def check_and_create(targetURL):
    al=algo()
    shortenURL,created_date='',''
    targetURL=targetURL.lower()
    if urlparse(targetURL).scheme=='':
        targetURL='http://'+targetURL
    link = models.Link.objects.filter(targetURL = targetURL)

    if link.count() == 0:
        link = models.Link()
        urlid = models.Link.objects.count()
        shortenURL = BASE_URL+al.encode(urlid)
        created_date = timezone.now()
        link.targetURL = targetURL
        link.shortenURL = shortenURL
        link.created_date = created_date
        link.save()
    else:
         link=link[0]
    return link

@login_required(login_url='/home/')
def shorten(request):
    form=forms.LinkForm()
    al=algo()
    shortenURL=''
    if request.method=='POST':
        form=forms.LinkForm(request.POST)
        if form.is_valid():
            targetURL=form.cleaned_data['targetURL']
            link = check_and_create(targetURL)
            shortenURL=link.shortenURL

    return render(request,'index.html',{'form':form,'shortenurl':shortenURL})


def target(request,URLid):
    #al=algo()
    #urlid=al.decode(URLid)+1
    shortURL = BASE_URL+URLid
    target = get_object_or_404(models.Link,shortenURL=shortURL)
    target.last_hit = timezone.now()
    target.hit_count += 1
    targetURL = target.targetURL
    lastHit = target.last_hit
    target.save()
    print('targetURL:',targetURL)
    print('lasthit:', lastHit)
    print('hit count:', target.hit_count)
    return HttpResponseRedirect(targetURL)


from basicapp import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication


class CreateAPI(APIView):
    serializer_class = serializers.LinkSerializer

    def post(self,request):
        serializer = serializers.LinkSerializer(data=request.data)
        if serializer.is_valid():
            targetURL = serializer.data.get('targetURL')
            link = check_and_create(targetURL)
            return Response({'created_date':link.created_date,'targetURL':link.targetURL,'shortenURL':link.shortenURL})
        else:
            return Response({'error':'error occured while making request'})
