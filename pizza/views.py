from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

def room(request):
    return render(request, 'pizza/room.html', {})
