from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import RegexValidator
from django.contrib.auth.models import User 
from django.conf import settings
from django.template.defaultfilters import truncatewords, truncatechars
import datetime
from time import sleep as _sleep
from django.db import connection

#from threading iimport Lock
@python_2_unicode_compatible
class Pool(models.Model):
	name = models.CharField(max_length=100,blank= False)
	active = models.BooleanField(default=False)
	def get_active_pool():
		active_pool = Pool.objects.get(id=2)
		#active_pool = Pool.objects.filter(active=True)[0]
		'''documents = active_pool.document_set.all()
		if len(documents)  > 5000:
			active_pool = False
			active_pool.save()
			try:
				active_pool = Pool.objects.get(id = active_pool.id+1)
				active_pool.active = True
				active_pool.save()
			except:
				active_pool = None
		'''
		return active_pool
	def __str__(self):
		return self.name

class Page(models.Model):
	page_id = models.PositiveIntegerField()
	page_url = models.URLField(max_length=2000)
	html_content = models.TextField()
	assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
	title = models.CharField(max_length=2000,blank= True)
	category =models.CharField(max_length=100,blank= False)
	category_kw_count = models.PositiveSmallIntegerField(default=0)
	def get_next_non_assigned_page():
		try:
#			pages = Page.objects.filter(title__icontains='census',assigned_user__isnull=True, category__icontains='pre_prod').order_by('-category_kw_count')[0]
			pages = Page.objects.filter(assigned_user=2)[0]
		except IndexError:
			try:
				pages = Page.objects.filter(assigned_user__isnull=True).order_by('category','-category_kw_count')[0]
			except IndexError:
				pages = None
		if pages:
			return pages
		else:	
			return None
	def __str__(self):
		return self.title
class Document(models.Model):
	text = models.TextField()
	page = models.ForeignKey('Page',on_delete=models.CASCADE)
	skip = models.BooleanField(default=False)
	exact_match_count = models.PositiveSmallIntegerField(default=0)
	has_table_reference = models.BooleanField(default=False)
	pool = models.ForeignKey('Pool',on_delete=models.SET_NULL,default=None, null=True)
	def page_id(self):
		return self.page.id
	def page_url(self):
		return self.page.page_url
	def short_text(self):
		return truncatewords(self.text,50)
	def assigned_user(self):
		return self.page.assigned_user
	def highlighted_text(self):
		text_hl = self.text
		offset =0
		for mention in self.mention_set.all().order_by('text_mention_start_offset'):
			if not mention.has_tables():
				continue
			update = '<span class="mention">' + mention.mention + '</span>'
			text_hl = text_hl[:offset+mention.text_mention_start_offset] + update + text_hl[offset+mention.text_mention_end_offset:]
			offset+= len(update) - len(mention.mention)
		return text_hl
	def completed(self):
		mentions = Mention.objects.filter(document=self,annotated=False, skip=False)
		if mentions is not None and len(mentions) >0:
			return False
		else:
			return True
	#answer = models.OneToOneField('EvaluationAnswer', on_delete=models.CASCADE)
	def __str__(self):
		return truncatewords(self.text,50)
class Table(models.Model):
	table_html = models.TextField()
	table_id = models.PositiveSmallIntegerField()
	nrows = models.PositiveSmallIntegerField()
	ncols = models.PositiveSmallIntegerField()
	ncells = models.PositiveSmallIntegerField()
	document = models.ForeignKey('Document',on_delete=models.CASCADE)
	caption =models.TextField(default='',null=True)
	referenced_in_text = models.BooleanField(default=False)	
	def short_table(self):
		return truncatewords(self.table_html,50)
	def __str__(self):
		return "Table id %d"%self.table_id
class Mention(models.Model):	
	mention = models.CharField(max_length=200)
	#mention_id =models.PositiveIntegerField()
	text_mention_start_offset = models.IntegerField()
	text_mention_end_offset = models.IntegerField()
	document = models.ForeignKey('Document',on_delete=models.CASCADE)
	annotated = models.BooleanField(default=False)
	skip = models.BooleanField(default=False)
	annotation_count = models.PositiveSmallIntegerField(default=0)
	locked = models.BooleanField(default=False)
	def has_tables(self):
		mention_tables = self.mention_table_set.all()
		return len(mention_tables) > 0
	def document__page_url(self):
		return self.document.page_url
	def document__page_id(self):
		return self.document.page_id	
	def highlighted_mention_in_text(self):
		# this is insane 
		text = self.document.text	
		result =text[:self.text_mention_start_offset] + '<span class="mention">' +  self.mention + '</span>' + text[self.text_mention_end_offset:]
		return result
	def __str__(self):
		return "id:{}, mention: {}".format(str(self.id),self.mention)
	def assigned_user(self):
		return self.document.page.assigned_user.id
class Mention_Table(models.Model):
	mention = models.ForeignKey('Mention',on_delete=models.CASCADE)
	table = models.ForeignKey('Table', on_delete=models.CASCADE)
	related = models.BooleanField(default=True)
	checked = models.BooleanField(default=False)

	 # this is set True by default as we consider all mentions_table pairs are related till somebody say's they are not!
	def mention__mention(self):
		return self.mention.mention
	def mention_id(self):
		return self.mention.id
	def document_id(self):
		return self.mention.document.id
	def document_page_url(self):
		return self.mention.document.page_url
	def document_page_id(self):
		return self.mention.document.page_id
	def highlighted_mention_in_text(self):
		text = self.mention.document.text
		result = text[:self.mention.text_mention_start_offset] + '<span class="mention">' +  self.mention.mention + '</span>' + text[ self.mention.text_mention_end_offset:]
		return result
	def table_view(self):
		return self.table.table_html
	def assigned_user(self):
		return self.mention.assigned_user
	@staticmethod
	def get_next_mention_table( user_id):
		number_annotated = Annotation.get_number_annotated(user_id)
		if  number_annotated > 6600:
			return -1
		if user_id.id ==3 or user_id.id ==14 or user_id.id == 6:
			return -1
	
		#pages = Page.objects.filter(assigned_user=user_id)
		#documents = Document.objects.filter(page__in =pages, skip = False)
		#documents  =  Document.objects.filter(skip = False, pool__active=True).order_by('page_id','-exact_match_count')
		mentions = Mention.objects.filter(locked = False,skip= False, annotation_count__lt = 3, document__skip =False, document__pool__active=True).order_by('-annotation_count', 'document__id','text_mention_start_offset')

		annotated_mentions_by_user = Annotation.objects.filter(annotator = user_id).exclude(relation ='Not Related').values('mention')

		mentions = mentions.exclude(id__in = annotated_mentions_by_user)

		#annotated_mentions_by_user  = Annotation.objects.filter(annotator = user_id).values('mention')
		#mentions = Mention.objects.filter(annotated = False,skip= False, annotation_count__lt = 3, document__skip =False, document__pool__active=True).order_by('document__id','text_mention_start_offset').select_related('mention_table')
		#mention_table = Mention_Table.objects.filter(mention__locked = False,mention__annotated = False,mention__skip= False, mention__annotation_count__lt = 3, mention__document__skip =False, mention__document__pool__active=True).order_by('mention__document__page__id','-mention__document__exact_match_count','mention__document__id','mention__text_mention_start_offset').exclude(mention__in = annotated_mentions_by_user)
		#.mention_table_set.exclude(mention_in = annotated_mentions_by_user)

		#mentions = Mention.objects.filter(annotated = False,skip= False, annotation_count__lt = 3, 
		#, document__in = documents).order_by('document__id','text_mention_start_offset')
		
		next_mention_table_id =-1
		for mention in mentions:
			not_related_tables = Annotation.objects.filter(annotator = user_id, mention=mention,relation ='Not Related').values_list("table",flat=True)
			mention_table_set = mention.mention_table_set.exclude(table__in = not_related_tables).order_by('id')
			if  len(mention_table_set)!= 0:
				next_mention_table_id = mention_table_set[0].pk 
				mention.locked = True
				mention.save()
				break
		return next_mention_table_id
	def __str__(self):
		return "Mention: %s, Table id: %d"% (self.mention.mention, self.table.table_id)
class Annotation(models.Model):
	exact = models.BooleanField()
	relation = models.CharField(max_length=100)
	related_table_cells = models.CharField(max_length=3000,validators=[
				RegexValidator(r'^([0-9]+,\s?)*$')
				])
	annotator =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	mention = models.ForeignKey('Mention', on_delete=models.CASCADE)
	table = models.ForeignKey('Table', on_delete=models.CASCADE,null=True)
	comment = models.CharField(max_length=500,null=True)
	updated = models.DateTimeField(auto_now = True)
	last_modified = models.DateTimeField(auto_now_add=True)
	ignore = models.BooleanField(default=False)

	get_annotations_disagreement_query='''
	select distinct userstudy_mention_table.id as mention_table_id, userstudy_mention.mention as mention
        from userstudy_annotation as annotation1
        inner join userstudy_annotation as annotation2 on annotation1.mention_id = annotation2.mention_id and annotation1.table_id = annotation2.table_id
        inner join userstudy_annotation as annotation3 on annotation1.mention_id = annotation3.mention_id and annotation1.table_id = annotation3.table_id
        inner join auth_user as annotator1 on annotation1.annotator_id = annotator1.id 
        inner join auth_user as annotator2 on annotation2.annotator_id = annotator2.id 
        inner join auth_user as annotator3 on annotation3.annotator_id = annotator3.id 
        inner join userstudy_mention_table on userstudy_mention_table.mention_id = annotation1.mention_id and  userstudy_mention_table.table_id = annotation1.table_id 
        inner join userstudy_mention on userstudy_mention.id = annotation1.mention_id
        where (annotation1.relation != annotation2.relation or  annotation2.relation != annotation3.relation or annotation2.relation != annotation3.relation )
        and (annotation1.related_table_cells != annotation2.related_table_cells or annotation1.related_table_cells != annotation3.related_table_cells or annotation2.related_table_cells != annotation3.related_table_cells)
        and annotation1.id >= annotation2.id and annotation2.id > annotation3.id
        and annotator1.id != annotator2.id and annotator1.id != annotator3.id and annotator2.id != annotator3.id
        and annotation1.ignore = False and annotation2.ignore = False and annotation3.ignore = False
        and userstudy_mention_table.checked = False;

	'''
	get_annotations_with_comments_query= '''
	select distinct userstudy_mention_table.id as mention_table_id, userstudy_mention.mention as mention
	from userstudy_annotation 
	inner join userstudy_mention_table on userstudy_mention_table.mention_id = userstudy_annotation.mention_id 
	and  userstudy_mention_table.table_id = userstudy_annotation.table_id 
	inner join userstudy_mention on userstudy_mention.id = userstudy_annotation.mention_id
	where comment not like '' and userstudy_mention_table.checked = False;
	'''

	get_single_annotations_query= '''
            select mention_table_id, mention from mention_ground_truth where count =1 and relation !='same';
	'''
	def get_single_annotated_mentions():
		result={}
		with connection.cursor() as cursor:
			cursor.execute(Annotation.get_single_annotations_query)
			result = Annotation.fetchdict(cursor)
		return result

	def get_annotations_with_comments():
		result={}
		with connection.cursor() as cursor:
			cursor.execute(Annotation.get_annotations_with_comments_query)
			result = Annotation.fetchdict(cursor)
		return result
	
	def get_annotations_disagreements():
		result ={}
		with connection.cursor() as cursor:
			cursor.execute(Annotation.get_annotations_disagreement_query)
			result = Annotation.fetchdict(cursor)
		return result
	def fetchdict(cursor):
		"Return all rows from a cursor as a dict"
		columns = [col[0] for col in cursor.description]
		#print(columns)
		
		data = [dict(zip(columns, row)) for row in cursor.fetchall()]
		#print(data)
		return data
	def get_all_annotations(mention_id,table_id):
		annotations = Annotation.objects.filter(mention__id = mention_id, table__id = table_id).all()
		#print( len(annotations))
		return annotations
	def get_number_annotated(user_id):
		annotations = Annotation.objects.filter(annotator=user_id).values("mention_id","table_id").distinct()
		#print( len(annotations))
		return len(annotations)
	def table_view (self):
		return self.table.table_html
	def annotator_name(self):
		return self.annotator.username
	def mention__mention(self):
		return self.mention.mention
	def relation_type(self):
		if self.exact:
			return "Exact"
		else:
			return "Approximate/Default"

	def __str__(self):
		if self.exact:
			return "Exact, %s, realted cells: %s"%(self.relation, self.related_table_cells)
		else:
			return "Approximate, %s, related cells %s "%(self.relation, self.related_table_cells)


