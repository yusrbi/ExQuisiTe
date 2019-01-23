# this code extract tables from a givenn html page
# it works with input string, however it is easy to get the html page and laod it as a string
import regex as re
from lxml import html,etree
from .table import Table
from .document import Document
from .mention_extractor import extract_mentions_from_text
from . import utils

class HtmlPage:
    def __init__(self,html_content):
        self.html_content = html_content
        self.title=''
        self.tables=[]
        self.content =''
        self.documents = None
        self.process_page(self.html_content)

    def get_all_tables(self):
        return self.tables

    def in_range(self, target,min,max):
        return target >=min and target <=max

    def get_header_content(self, header_cells):
        content =[]
        for header in header_cells:
            for br in header.xpath('.//br'):
                br.tail = " " + br.tail if  br.tail else " "
            content.append(header.text_content().strip().lower())
        return content
    def get_caption_content(self,cap):
        content = ''
        for tag in cap:
            content = content + self.get_tag_content(tag)
        return content

    def get_tag_content(self,tag):
        for br in tag.xpath(".//br"):
            br.tail = " " + br.tail if br.tail else " "
        content =  tag.text_content().strip().lower()
        return content
    def process_page(self, html_content):
        #This function
        #try:
        root = html.document_fromstring(html_content)
        #except:
        #    return
        titles = root.xpath("//title")
        for title in titles:
            self.title = title.text_content()
            break
        tables = root.xpath('//table')
        table_id =0
        for table in tables:
            if table.xpath('.//table')!=[]:
            #skip table that has nasted tables
                continue
            else:
                table_id+=1
                table_obj = Table(table_id,table_id, etree.tostring(table).decode("utf-8"),'')
                if table_obj.consider_table: #if the table hs nrows and ncols > 1 in addition to at least 30% quantity cells
                    self.tables.append(table_obj)
                table.getparent().remove(table)# remove the table content from the page content
            # remove the scripts from the page content
            scripts = root.xpath('//script')
            if scripts:
                for script in scripts:
                    script.getparent().remove(script)
            styles = root.xpath('//style')
            if styles:
                for style in styles:
                    style.getparent().remove(style)
            self.content = root.text_content()

    def create_documents(self):
                #create documents of text and related tables
        documents = self.process_text_to_documents(self.content)
        self.documents = documents
        return documents
    def has_number(self,text):
        match = re.search(r"([\d\%\$\.\,\-]+)",text)
        if match:
            return True
        else:
            return False

    def count_char(self,text, c):
        count =0 
        for ch in text:
            if ch ==c:
                count+=1
        return count

    def process_text_to_documents(self,text):
        text_blocks = re.split(r'(?:[\.\;](?:\n|\r\n|\r)|(?:\n|\r\n|\r){2,})',text)
        doc_id =0
        docs =[]
        #check on a single \n ommit all the lists!
        for block in text_blocks:
            block = re.sub('\s{2,}',' ', block.strip())
            if block is '' or not self.has_number(block):
                continue
            #if len(block)< 100 or len(block)>1000:
            #   continue
            if self.count_char(block,'\n') > 4:
                continue # most likely it is a list
            #block = re.sub(r'\r\n|\n',' ', block)
            #print(block)
            mentions = extract_mentions_from_text(block)
            if len(mentions)<1:
                continue
            doc_id = doc_id +1
            document = Document(0, doc_id, block)
            document.add_mentions(mentions)
            document_tokens = utils.get_word_set(block)
            cand_tables=[]
            for table in self.tables:
                overlap_coef = utils.get_tokens_overlap(document_tokens, table.general_context_tokens)
                if overlap_coef >= 0.2:
                    cand_tables.append(table)
            document.add_tables(cand_tables)
            docs.append(document)
        return docs

    def get_documents_as_text(self):
        text =''
        for document in self.documents:
            doc_text, related_tables = document.get_text_with_mentions()
            if not related_tables:
                continue
            text = "%s \n <h2> Document ID:%d</h2>, <p>Document text: %s</p>"%(text, document.doc_id,doc_text)
            for table in document.tables:
                if table.table_id in related_tables:
                    text = "%s,\n<h3> table id:%s,\n</h3>  <div name=\"target-table-%s\" class=\"table\"> table: %s</div>"%(text, table.table_id, table.table_id, table.get_table_content())
        return text

def test():
    html_page =''' <html>
<head>
<title>Test Page</title>
</head>
<body>
<table border="0" cellpadding="0" cellspacing="3" width="650">
                <tbody><tr>
                    <td width="175"></td>
                    <th width="130">
                        <div align="center">
                            Killed in Action</div>
                    </th>
                    <th width="130">
                        <div align="center">
                            Died of Wounds</div>
                    </th>
                    <th width="130">
                        <div align="center">
                            Wounded in Action</div>
                    </th>
                    <th width="85">
                        <div align="center">
                            Totals</div>
                    </th>
                </tr>
                <tr>
                    <td width="175">
                        <div align="center">
                        2005</div>
                    </td>
                    <td width="130">
                        <div align="center">
                             7</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            unknown</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            14</div>
                    </td>
                    <td width="85">
                        <div align="center">
                            23</div>
                    </td>
                </tr>
                <tr>
                    <td width="175">
                        <div align="center">
                            2013</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            -</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            -</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            3</div>
                    </td>
                    <td width="85">
                        <div align="center">
                            3</div>
                    </td>
                </tr>
                <tr>
                    <td width="175">
                        <div align="center">
                            Bluejackets</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            17</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            2</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            51</div>
                    </td>
                    <td width="85">
                        <div align="center">
                            70</div>
                    </td>
                </tr>
                <tr>
                    <td width="175">
                        <div align="center">
                            Marine Corps Enlisted Men</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            47</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            -12</div>
                    </td>
                    <td width="130">
                        <div align="center">
                            +139</div>
                    </td>
                    <td width="85">
                        <div align="center">
                            198</div>
                    </td>
                </tr>
                <tr>
                    <td width="175">
                        <div align="center">
                            <b>Totals</b></div>
                    </td>
                    <td width="130">
                        <div align="center">
                            <b>71</b></div>
                    </td>
                    <td width="130">
                        <div align="center">
                            <b>16%</b></div>
                    </td>
                    <td width="130">
                        <div align="center">
                            <b>207</b></div>
                    </td>
                    <td width="85">
                        <div align="center">
                            <b>$294</b></div>
                    </td>
                </tr>
                <tr>
                <td> </td>
                <td> </td>
                <td> </td>
                <td> _  </td>
                </tr>
            </tbody>
            <tfoot>
                <tr>
                <td> Hello Footer </td>
                <td> another Footer </td>
                </tr>
            </tfoot>
            <caption> Table 1 h a Caption is given!</caption>
        </table>
    this is the only content
    <script type="text/javascript" src="/static/admin/js/vendor/xregexp/xregexp.js"></script>

</body>
</html>
'''

    page = HTMLPage(html_page)
    print(page.content)
    print(page.title)
    for table in page.tables:
        print("Table nRows:%d, nColumns:%d, nCells:%d, nQCells: %d"%(table.nrows,table.ncolumns,table.ncells,table.nquantity_cells))
        print("Table by rows:")
        print(table.content_by_row)
        print("Word set:")
        print(table.word_set)
        print("Header:")
        print (table.header)
        print("Quantity %")
        print (table.get_percent_qmentions())
        print("Quantities")
        print (table.quantities)
        print(table.caption_contains('Table 2'))
        print("Table Footer")
        print(table.footer)
        print("Caption:")
        print(table.caption)
        print("ncells")
        print(table.ncells)
    print(page.get_tables(0,20,20,30,10,220,0.5))
    print(page.get_all_tables())

if __name__=='__main__':
    test()
