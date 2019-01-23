from django.contrib import admin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from .models import Document, Mention,Mention_Table, Annotation, Table, Page,Pool
# Register your models here.

class DocumentInline(admin.StackedInline):
	model = Document
class PageInline(admin.StackedInline):
	model = Page
class AnnotationInline(admin.TabularInline):
	model = Annotation
class PageAdmin(admin.ModelAdmin):
	model = Page
	list_display=['page_url','title','assigned_user','category','category_kw_count']
	list_filter=['assigned_user','category']
	search_fields=['title']
	inlines =[DocumentInline,]
class Mention_TableAdmin (admin.ModelAdmin):
	model = Mention_Table
	list_display =['mention', 'document_page_url','document_page_id']	
#	inlines=[AnnotationInline]
	search_fields=['document_page_id']
	list_filter=['mention__annotated','related']
class TableInLine(admin.TabularInline):
	model = Table
	extra = 2
class MentionInline(admin.TabularInline):
	model = Mention
	extra=5
	search_fields=['mention']

class DocumentListFilter(admin.SimpleListFilter):
	title = _('Document Status')
	parameter_name = 'status'
	def lookups(self,request,model_admin):
		return (('True', _('Completed')),
			('False', _('Not Completed')))
	def queryset(self,request,queryset):

		if self.value() =='True':
			documents = queryset.exclude(mention__skip =False,mention__annotated =False)
		else:
			documents = queryset.filter(mention__skip =False,mention__annotated = False)
		return documents.distinct()
	
class DocumentAdmin(admin.ModelAdmin):
	model = Document
	list_display=['page_url','short_text','pool']
	inlines=[MentionInline,TableInLine]
	search_fields=['text']
	list_filter=[DocumentListFilter,'pool']

class PoolAdmin(admin.ModelAdmin):
	model = Pool
	list_display = ['name']
	
admin.site.register(Document,DocumentAdmin)
admin.site.register(Mention_Table, Mention_TableAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Pool,PoolAdmin)
