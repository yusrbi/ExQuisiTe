from django.conf.urls import  url 
from . import views 
app_name='userstudy'
urlpatterns=[

	url(r'^$',views.HomePageView.as_view(), name='home'),
	url(r'^(?P<pk>[0-9]+)/$',views.MentionDetailView.as_view(), name='detail'),
	url(r'^(?P<mention_table_id>[0-9]+)/submit$',views.submit_answer, name='submit_answer'),
	url(r'^done$', views.DoneView.as_view(), name='all_done'),
	url(r'^next$', views.next_mention_table, name='next'),
	url(r'^manual', views.AnnotationManual.as_view(), name='annotation_manual'),
	url(r'^page/(?P<page_id>[0-9]+)/$', views.page_view, name='page_view'),
	url(r'^pagepreview/(?P<pk>[0-9]+)/$', views.PagePreviewView.as_view(), name='page_preview'),
	url(r'^document/(?P<document_id>[0-9]+)/skip$', views.skip_document, name='skip_document'),
	url(r'^mention/(?P<mention_id>[0-9]+)/skip$', views.skip_mention, name='skip_mention'),
	url(r'^assignuser/(?P<page_id>[0-9]+)/', views.assign_user, name="assign_user"),
	url(r'^imprint$', views.ImprintView.as_view(), name="imprint"),
	url(r'^dataprotection', views.DataProtectionView.as_view(), name ="data_protection"),
	url(r'^selectdocument/(?P<page_id>[0-9]+)/', views.add_documents_to_batch, name="select_document"),
	url(r'^endsession/(?P<mention_id>[0-9]+)/', views.end_session, name="end_session"),
	url(r'^mentionannotationview/(?P<pk>[0-9]+)/$', views.MentionAnnotationView.as_view(), name="mention_annotation"),
	url(r'^annotatedmentionlist/', views.list_annotated_mentions, name="list_annotated_mentions"),
	url(r'^ignoreannotation/(?P<pk>[0-9]+)/$', views.ignore_annotation, name="ignore_annotation"),
	url(r'^considerannotation/(?P<pk>[0-9]+)/$', views.consider_annotation, name="consider_annotation"),
	url(r'^mentiontabledone/(?P<pk>[0-9]+)/$', views.mention_table_done, name="mention_table_done"),
	url(r'^annotationswithcomments/', views.list_annotations_with_comments, name ="list_annotations_with_comments"),
        url(r'^singleannotations/', views.list_single_annotations, name ="list_single_annotations"),

]

