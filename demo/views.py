from django.shortcuts import render
from django.views import generic
from .forms import UploadFileForm,PlainTextInputForm,URLForm,SelectInputForm
from django.http import HttpResponseRedirect
from .processor import process_url, process_html
from django import forms


# Create your views here.

class HomePageView(generic.base.TemplateView):
    template_name ="demo/home.html"



def select_input(request):
    text_input ='txt'
    url_input = 'url'
    html_input = 'html'
    error =''
    target_form = None
    if request.method == 'POST':
        form = SelectInputForm(request.POST)
        if form.is_valid():
            threshold = form.cleaned_data['threshold']
            adaptive_filter = form.cleaned_data['adaptive_filtering']
            algorithm = form.cleaned_data['algorithm']
            input_type = form.cleaned_data['input_choice']
            if input_type == text_input:
                target_form = PlainTextInputForm()
                target_template = 'demo/text-engine.html'
            elif input_type == url_input:
                target_form = URLForm(initial={'algorithm': algorithm, 'threshold':threshold, 'adaptive_filtering':adaptive_filter})
                target_template = 'demo/url-engine.html'
            elif input_type == html_input:
                target_form = UploadFileForm(initial={'algorithm': algorithm, 'threshold':threshold, 'adaptive_filtering':adaptive_filter})
                target_template = 'demo/file-engine.html'
            
            print("settings1:", algorithm, threshold, adaptive_filter)

            # target_form.fields['algorithm'].initial = algorithm
            # target_form.fields['threshold'].initial = threshold
            # target_form.fields['adaptive_filtering'].initial = adaptive_filter

            target_form.fields['algorithm'].widget = forms.HiddenInput()
            target_form.fields['threshold'].widget = forms.HiddenInput()
            target_form.fields['adaptive_filtering'].widget = forms.HiddenInput()

    if not target_form:
        target_form = SelectInputForm(initial={'input_choice': html_input})
        return render(request, 'demo/input-engine.html', {'form':target_form})
    else:
        return render(request, target_template ,{'form':target_form})

def process_plain_text(request):
    if request.method == 'POST':
        form = PlainTextInputForm(request.POST, request.FILES)
        results = None

        if form.is_valid():
            text = form.cleaned_data['plain_text']
           
    else:
        target_form = SelectInputForm(initial={'input_choice': html_input})
        return render(request, 'demo/input-engine.html', {'form':target_form})


def process_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        results = None

        if form.is_valid():
            file_data = request.FILES['file']
            #threshold = form.cleaned_data['threshold']
            threshold = form.cleaned_data['threshold']
            algorithm = form.cleaned_data['algorithm']
            adaptive_filtering = form.cleaned_data['adaptive_filtering'] 
            print("settings:", algorithm, threshold, adaptive_filtering)
            if algorithm == 'RWR':
                rwr_algorithm = True
            else:
                rwr_algorithm = False
            results = process_html(file_data.read().decode("utf-8"), 
                threshold=threshold, rwr_algorithm = rwr_algorithm, adaptive_filtering= adaptive_filtering)
            if results:
                return render(request,'demo/show_results.html', {'results':results})
            else:
                return render(request, 'demo/problem.html', {'error' : "Error Message"})    
        else:
            print(form.fields['algorithm'].initial, form.fields['threshold'].initial, form.fields['adaptive_filtering'].initial) 
           
    else:
        target_form = SelectInputForm(initial={'input_choice': html_input})
        return render(request, 'demo/input-engine.html', {'form':target_form})

def process_url(request):
    if request.method == 'POST':
        form = URLForm(request.POST, request.FILES)
        results = None

        if form.is_valid():
            url = form.cleaned_data['url']
            threshold = form.fields['threshold'].initial 
            algorithm = form.fields['algorithm'].initial 
            adaptive_filtering = form.fields['adaptive_filtering'].initial 
            if algorithm == 'RWR':
                rwr_algorithm = True
            else:
                rwr_algorithm = False
            results = process_url(url,  threshold=threshold, rwr_algorithm = rwr_algorithm, adaptive_filtering= adaptive_filtering)
            if results:
                return render(request,'demo/show_results.html', {'results':results})
            else:
                return render(request, 'demo/problem.html', {'error' : "Error Message"})     
           
    else:
        target_form = SelectInputForm(initial={'input_choice': html_input})
        return render(request, 'demo/input-engine.html', {'form':target_form})



def process_input(request):
    error =''
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        results = None

        if form.is_valid():
            file_data = request.FILES['file']
            url = form.cleaned_data['url']
            if file_data:
                if file_data.content_type !='text/html':
                    error = "wrong file type!"
                    return render(request, 'demo/engine.html',{'form':form,'error':error})
                results = process_html(file_data.read())
            elif url:
                results = process_url(url)
        if results:
            return render(request,'demo/show_results.html', {'results':results})
        else:
            return render(request, 'demo/problem.html', {'error' : "Error Message"})

    else:
        form = UploadFileForm()
        return render(request, 'demo/engine.html',{'form':form})


