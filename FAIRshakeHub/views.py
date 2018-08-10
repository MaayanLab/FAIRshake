from django.shortcuts import render

def index(request):
  ''' FAIRshakeHub Home Page
  '''
  return render(request, 'fairshake/index.html')

def bookmarklet(request):
  return render(request, 'fairshake/bookmarklet.html')

def chrome_extension(request):
  return render(request, 'fairshake/chrome_extension.html')
