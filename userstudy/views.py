from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect 
from django.views import generic
from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login,authenticate
from django.db.models import Q
from django.urls import reverse
from .models import Page,Document, Mention, Annotation, Mention_Table, Pool 	
from django.contrib.auth.models import User
from threading import Lock
from django.contrib.auth import logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django import template
from django.template.defaulttags import register

lock = Lock()


@register.filter(name='get_item')
def get_item(dictionary, key):
	return dictionary[key]
@login_required
def list_annotated_mentions(request):

	mention_tables = Annotation.get_annotations_disagreements()
	paginator = Paginator(mention_tables, 100)	
	page = request.GET.get('page')
	try:
		mention_tables = paginator.page(page)
	except PageNotAnInteger:
	# If page is not an integer, deliver first page.
		mention_tables = paginator.page(1)
	except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        	mention_tables = paginator.page(paginator.num_pages)
	return render(request, 'userstudy/list_annotated_mentions.html', {'mention_tables': mention_tables})


@login_required 
def list_single_annotations(request):
	mention_tables = Annotation.get_single_annotated_mentions()
	paginator = Paginator(mention_tables,100)
	page = request.GET.get('page')
	try:
		mention_tables = paginator.page(page)
	except PageNotAnInteger:
		mention_tables = paginator.page(1)
	except EmptyPage:
		mention_tables = paginator.page(paginator.num_pages)
	return render(request, 'userstudy/list_annotated_mentions.html', {'mention_tables': mention_tables})

@login_required 
def list_annotations_with_comments(request):
	mention_tables = Annotation.get_annotations_with_comments()
	paginator = Paginator(mention_tables,100)
	page = request.GET.get('page')
	try:
		mention_tables = paginator.page(page)
	except PageNotAnInteger:
		mention_tables = paginator.page(1)
	except EmptyPage:
		mention_tables = paginator.page(paginator.num_pages)
	return render(request, 'userstudy/list_annotated_mentions.html', {'mention_tables': mention_tables})

@login_required
def page_view(request,page_id):
	page = get_object_or_404(Page, pk = page_id)
	return HttpResponse(page.html_content)


@login_required
def skip_mention(request, mention_id):
	mention= get_object_or_404(Mention, pk = mention_id)
	mention.skip = True
	mention.locked = False
	mention.save()
	return HttpResponseRedirect(reverse('userstudy:next'))
@login_required
def skip_document(request, document_id):
	document = get_object_or_404(Document, pk =document_id)
	document.skip = True
	document.save()
	return HttpResponseRedirect(reverse('userstudy:next'))
class ImprintView(generic.base.TemplateView):
	template_name = "userstudy/imprint.html"
class DataProtectionView(generic.base.TemplateView):
	template_name = "userstudy/data_protection.html"
	
class HomePageView(generic.base.TemplateView):
	template_name ="userstudy/home.html"
#	def get_context_data(self, **kwargs):
#        	context = super(HomePageView, self).get_context_data(**kwargs)
#        	context['latest_articles'] = Article.objects.all()[:5]
#        	return conte

#def index(request):
#	return HttpResponse("Hello, World!")

class DoneView(generic.base.TemplateView):
	template_name ="userstudy/done.html"
class AnnotationManual(generic.base.TemplateView):
	template_name = "userstudy/annotation_manual.html"

class PagePreviewView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
	model = Page
	template_name ='userstudy/page_preview.html'
	permission_required =('userstudy.change_page','userstudy.delete_page', 'userstudy.delete_document', 'userstudy.change_document')
	
	def get_context_data(self, **kwargs):
		context = super(PagePreviewView,self).get_context_data(**kwargs)
		context['user'] = self.request.user
		context['users'] = User.objects.all()
		return context
class MentionAnnotationView(LoginRequiredMixin, PermissionRequiredMixin, generic.DetailView):
	model = Mention_Table
	template_name='userstudy/mention_annotation.html'
	permission_required = ('userstudy.change_annotation', 'userstudy.delete_annotation')
	def get_context_data(self, **kwargs):
		context = super(MentionAnnotationView,self).get_context_data(**kwargs)
		context['annotations']= Annotation.get_all_annotations(context['mention_table'].mention.id, context['mention_table'].table.id)
		if 'HTTP_REFERER' in self.request.META:
			ref = self.request.META['HTTP_REFERER']
			#print(ref)
		else:
			ref=''
		
		if "mentionannotationview" in ref or 'annotatedmentionlist' in ref:
			#print("ref contains mentionannotationview or annotatedmentionlist")
			context['load_next'] = 'False'
		else:
			context['load_next'] = 'True'
		#print(context)
		return context 		

@login_required
def ignore_annotation(request, pk):
	annotation = get_object_or_404(Annotation, pk= pk)
	annotation.ignore = True
	annotation.save()
	return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def consider_annotation(request, pk):
	annotation = get_object_or_404(Annotation, pk= pk)
	annotation.ignore = False
	annotation.save()
	return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def mention_table_done(request, pk):
	mention_table = get_object_or_404(Mention_Table, pk=pk)
	mention_table.checked = True
	mention_table.save()
	return HttpResponseRedirect(reverse('userstudy:list_single_annotations'))
    #HttpResponseRedirect(reverse('userstudy:list_annotations_with_comments')) #HttpResponseRedirect(reverse('userstudy:list_annotated_mentions'))


def add_documents_to_batch(request, page_id):
	page = get_object_or_404(Page, pk=page_id)
	#page.assigned_user = request.user
	#page.save()
	
	document_id_list = request.POST['document_id_list']
	action = request.POST['submit_page']
	pool = None
	if action == 'Boring Numbers':
		pool = Pool.objects.get(id =3)
	else:
		pool = Pool.get_active_pool()
	if not pool:
		return HttpResponseRedirect(reverse('userstudy:all_done'))
	if action != 'Ignore':
		page.assigned_user = request.user
		page.save()
		for document_id in document_id_list.split(','):
			if len(document_id.strip()) ==0:
				continue
			#print(document_id)
			document = Document.objects.get(id =int(document_id))
			document.pool = pool
			document.save()
	else:
		page.assigned_user = User.objects.get(id=11)
		page.save()

	next_page = Page.get_next_non_assigned_page()
	if next_page:
		return HttpResponseRedirect(reverse('userstudy:page_preview',args=(next_page.id,)))
	else:
		return HttpResponseRedirect(reverse('userstudy:all_done'))
def assign_user(request, page_id):
	page = get_object_or_404(Page, pk=page_id)
	user_id = request.POST['user_id']
	user = get_object_or_404(User, pk=user_id)
	page.assigned_user = user
	page.save()
	next_page = Page.get_next_non_assigned_page()
	if next_page:
		return HttpResponseRedirect(reverse('userstudy:page_preview',args=(next_page.id,)))
	else:
		return HttpResponseRedirect(reverse('userstudy:all_done'))
class MentionDetailView(LoginRequiredMixin,PermissionRequiredMixin ,generic.DetailView):
	model= Mention_Table
	template_name='userstudy/detail.html'
	permission_required = ('userstudy.add_annotation', 'userstudy.change_annotation',"userstudy.change_document", "userstudy.change_mention_table")
	
	def get_context_data(self, **kwargs):
		context = super(MentionDetailView, self).get_context_data(**kwargs)
		context['user'] = self.request.user
		annotation_count = Annotation.get_number_annotated(self.request.user.id) 
		#print(annotation_count)
		context['annotated_mentions'] = annotation_count
		if 'HTTP_REFERER' in self.request.META:
			ref = self.request.META['HTTP_REFERER']
		else:
			ref=''
		if "mentionannotationview" in ref:
			context['load_next'] = False
		else:
			context['load_next'] = True

		return context
@login_required 
def next_mention_table(request):
	next_mention_table_id = Mention_Table.get_next_mention_table(request.user)
	if( next_mention_table_id != -1):
		return HttpResponseRedirect(reverse('userstudy:detail',args=(next_mention_table_id,)))
	else:
		return HttpResponseRedirect(reverse('userstudy:all_done'))
@login_required 
def end_session(request, mention_id):
	mention = get_object_or_404(Mention, pk=mention_id)
	mention.locked = False
	mention.save()
	logout(request)
	return HttpResponseRedirect(reverse('userstudy:home'))
@login_required 
def submit_answer(request, mention_table_id):
	global lock
	mention_table  = get_object_or_404(Mention_Table,pk=mention_table_id)
	try:
		#print(request.POST)
		submit_btn = request.POST['submit_btn']
		#print(submit_btn)
		relation = request.POST['relation']
		load_next = request.POST['load_next']
		if load_next == 'True':
			load_next = True
		else:
			load_next = False

		if submit_btn ==  'Not a Mention':
			relation = 'Not Mention'
		elif submit_btn == 'Not Related':
			relation = 'Not Related'
		#print(relation)
		if relation == 'other':
			relation = request.POST['other_aggregate']
		if submit_btn == 'Exact':
			exact = 'True'
		else:
			exact = 'False'
		table_cells = request.POST['related_cells']
		#exact = request.POST['exact']
		user = request.user
		comment = request.POST['comment']
		if not (user.has_perm("userstudy.add_annotation") and user.has_perm("userstudy.change_document") and user.has_perm("userstudy.change_mention_table") ):
			return HttpResponseRedirect(reverse('userstudy:home'))
		#CREATE A NEW ANNOTaTION
		annotation = Annotation.objects.create(mention = mention_table.mention, table = mention_table.table, exact=exact,relation=relation,related_table_cells =table_cells, annotator= user,comment=comment)
		mention = mention_table.mention
		if relation != 'Not Related':
			#in case the relation is not a mention or sum, avg, max,etc.
			#mark all other mention_table pairs as unrelated
			#add an extra annoattion count 
			mention.annotation_count +=1
			if mention.annotation_count >=3:
				mention.annotated = True
			mention.save()
			mention_table_set=mention.mention_table_set.exclude(pk=mention_table_id)
			for mention_table_obj in mention_table_set:
				#if mention_table_obj.pk != mention_table_id:
				mention_table_obj.related= False
				mention_table_obj.save()

	#		mention_table.related=True
		else:# No related, mark this mention_table pair only as not related
			mention_table.related=False
			mention_table.save()
			related_mention_tables = mention.mention_table_set.filter(related= True)
			if not related_mention_tables or len(related_mention_tables) ==0:
				mention.annotation_count +=1
				if mention.annotation_count >=3:
					mention.annotated = True
				mention.save()
		mention.save()
	except KeyError as e:
		if mention_table:
			mention = mention_table.mention
			mention.locked = False
			mention.save()
		return render(request,'userstudy/detail.html',{
			'mention_table': mention_table,
			'error_message': "Error occurred while submitting your answer,  %s is not provided in POST, Please contact your supervisor"%e,
			})
	else:
		#get the next mention for that user 
		#should call the model to get the next mention in the queue
		if mention_table:
			mention = mention_table.mention
			mention.locked = False
			mention.save()
		if not load_next:
			print(request.META['HTTP_REFERER'])
			return HttpResponseRedirect(reverse('userstudy:mention_annotation',args=(mention_table_id,)))	
		with lock:
			next_mention_table_id = Mention_Table.get_next_mention_table(request.user)
		
		if(next_mention_table_id !=-1):
			return HttpResponseRedirect(reverse('userstudy:detail',args=(next_mention_table_id,)))
		else:
			return HttpResponseRedirect(reverse('userstudy:all_done'))
	finally:
		if mention_table:
			mention = mention_table.mention
			mention.locked = False
			mention.save()
