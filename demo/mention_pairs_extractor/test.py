
import codecs
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'demo')))
sys.path.append(os.path.abspath(".."))

from html_page import HtmlPage
from demo.processor import process_html

file = codecs.open("mention_pairs_extractor/test2.html", "r", "utf-8")
html_content = file.read()
results_text = process_html(html_content)["results"]
#html_page = HtmlPage(html_content, 0)
#documents = html_page.create_documents()
#results_text = html_page.get_html_with_annotations()

with codecs.open("mention_pairs_extractor/test2_proc.html", "w+","utf-8") as file:
	file.write(results_text.decode("utf-8"))


