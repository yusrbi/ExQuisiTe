from userstudy.models import Mention_Table

Mention_Table.get_next_mention_table(1)

from userstudy.models import Mention_Table
Mention_Table.get_next_mention_table(1)
from userstudy.models import Document, Pool, Page, Mention, Table
Pool.Create(name="Batch1", active=True)
batch1 = Pool.objects.create(name="Batch1", active=True)
doc1 = Document.objects.get(id =40910)
doc1.mention_set.all().values("annotated","skip")
batch1.document_set.add(doc1)
doc2 = Document.objects.get(id =58790)
doc2.mention_set.all().values("annotated","skip")
Mention_Table.get_next_mention_table(1)
# 16 
#add an annotation \\


 mention_table = Mention_Table.objects.filter(mention__annotated = False,mention__skip= False, mention__annotation_count__lt = 3, mention__document__skip =False, mention__document__pool__active=True).order_by('mention__document__page__id',    '-mention__document__exact_match_count','mention__document__id','mention__text_mention_start_offset').exclude(id__in = annotated_mentions_by_user)

annotated_mentions_by_user  = Annotation.objects.filter(annotator = 4).values('mention')

annotated_mentions_by_user.all()

# add annottaion 

