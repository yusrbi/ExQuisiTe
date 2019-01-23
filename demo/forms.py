from django import forms
from django.core import validators 
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Div, Field, Row, Column

from django.urls import reverse 

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Upload File", required=True)
    algorithm = forms.CharField( required = False)
    threshold = forms.FloatField( min_value = 0.0, max_value = 1.0, required= False)
    adaptive_filtering = forms.BooleanField( required = False)

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "input-document"
        #self.helper.form_class = "demo-form"
        self.helper.form_method="POST"
        self.helper.form_action = reverse("demo:process_file")
        #self.helper.add_input(Submit('submit','Submit'))
        #self.helper.label_class = 'col-sm-2'
        #self.helper.field_class = 'col-sm-5'
        #self.threshold =threshold

        self.helper.layout = Layout(
            Row(
                Column('file', css_class='form-group col-sm-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Submit'),
            Row(
                Column('algorithm'), Column('threshold'), Column('adaptive_filtering')
                )
        )
    #url  = forms.CharField(label="URL:", required=False,validators=[validators.URLValidator(schemes=['http','https'])])

   




class URLForm(forms.Form):
    url  = forms.CharField(label="URL:", required=True,validators=[validators.URLValidator(schemes=['http','https'])])
    #self.helper.add_input(url)
    algorithm = forms.CharField(required = False)
    threshold = forms.FloatField( min_value = 0.0, max_value = 1.0, required= False)
    adaptive_filtering = forms.BooleanField( required = False)

    def __init__(self, *args, **kwargs):
        super(URLForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "input-url"
        #self.helper.form_class = "demo-form"
        self.helper.form_method="POST"
        self.helper.form_action = reverse("demo:process_url")
        #self.helper.add_input(Submit('submit','Submit'))
        #self.helper.label_class = 'col-sm-2'
        #self.helper.field_class = 'col-sm-5'
        self.helper.layout = Layout(
            Row(
                Column('url', css_class='form-group col-sm-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Submit')
        )
  


    


class PlainTextInputForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PlainTextInputForm,self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id ='input-plain-text'
        #self.helper.form_class = 'demo-form'
        self.helper.form_method ='POST'
        self.helper.from_action = reverse("demo:process_plain_text")
        self.helper.add_input(Submit('submit', 'Submit'))
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-5'
    plain_text = forms.CharField(label ="Text",  widget=forms.Textarea, required= True)
    #self.helper.add_input(plain_text)
    

class SelectInputForm(forms.Form):
    text_input ='txt'
    url_input = 'url'
    html_input = 'html'
        
    input_choices = ( #(text_input, 'Plain Text Input'),
            (url_input, 'Page URL'),
            (html_input, 'HTML File')
            )

    input_choice = forms.ChoiceField(label ="Input Type", choices =input_choices, required= True, widget=forms.Select)
    #self.helper.add_input(input_choice)
    #options
   
    #collective algorithm
    algorithms_choices =( ('RWR', "Random Walk with Restart"),
                  ('None', "No Global Resolution")
        )
        
    algorithm = forms.ChoiceField(label ="Algorithm", choices =algorithms_choices, required= True, widget=forms.Select)
 #threshold
    threshold = forms.FloatField(label="Threshold", min_value = 0.0, max_value = 1.0, required= True, initial=0.5, 
        widget=forms.NumberInput(attrs={'step': "0.1"}))

    #use adaptive filtering 

    adaptive_filtering = forms.BooleanField(label ="Adaptive Filtering", initial=True, required=False)
    def __init__(self, *args, **kwargs):
        
        self.helper = FormHelper()
        self.helper.form_id ='select-input'
        #self.helper.form_class = 'demo-form'
        self.helper.form_style= 'inline'
        self.helper.form_method ='POST'
        self.helper.from_action = reverse("demo:select_input")
        #self.helper.add_input(Submit('submit', 'Go >'))
        #self.helper.label_class = 'col-sm-2'
        #self.helper.field_class = 'col-sm-5'
      
        self.helper.layout = Layout(
            Row(
                Column('input_choice', css_class='form-group col-sm-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('algorithm', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('threshold', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('adaptive_filtering', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'GO >')
        )
      
        # self.helper.layout = Layout(
        #     Div('input_choice', css_class="container"),
        #     Fieldset(
        #         'Options',
        #         'algorithm',
        #         'threshold',
        #         'adaptive_filtering'
        #     ),
        #     ButtonHolder(
        #         Submit('submit', 'Go >')
        #     )
        # )
        super(SelectInputForm,self).__init__(*args, **kwargs)


   


