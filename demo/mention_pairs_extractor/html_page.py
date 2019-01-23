# this code extract tables from a givenn html page
# it works with input string, however it is easy to get the html page and laod it as a string
import regex as re
from lxml import html,etree
from .table import Table
from .document import Document
from .mention_extractor import extract_mentions_from_text
from .utils import  get_word_set, get_tokens_overlap
import traceback
from  io import StringIO
class HtmlPage:
    def __init__(self,html_content, index):
        self.html_content = html_content
        self.title=''
        self.tables=[]
        self.content =''
        self.documents = None
        self.mentions_count =0
        self.row_count =0
        self.col_count =0
        self.qcell_count =0
        self.vcell_count =0 

        self.process_page(self.html_content)
        self.index = index
        
        print("page object created for page %s"%index)
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
        try:
            #tree = html.parse(StringIO(html_content))
            #root = tree.getroot()
            root = html.document_fromstring(html_content)
        except(Exception) as error:
            print(error)
            return
        titles = root.xpath("//title")
        for title in titles:
            self.title = title.text_content()
            break
        tables = root.xpath('//table')
        table_id =0
        for table in tables:
            if table.xpath('.//table'):
            #skip table that has nasted tables
                continue
            else:
                table_id+=1
                table_xpath_id = self.get_path(table, root)
                try:
                    #print(table.text_content())
                    table_obj = Table(table_id,table_id, html.tostring(table, method="html", encoding="UTF-8", pretty_print= True).decode("utf-8"),'')
                except(Exception) as error:
                    print("Error parsing table %s"% error)
                    traceback.print_exc()
                    continue
                print("table object created")
                if table_obj.consider_table: #if the table hs nrows and ncols > 1 in addition to at least 30% quantity cells
                    print("consider table")
                    self.tables.append(table_obj)
                    self.row_count  = self.row_count+ table_obj.row_count
                    self.col_count = self.col_count + table_obj.col_count
                    self.qcell_count = self.qcell_count + table_obj.get_mentions_count()
                    self.vcell_count = self.vcell_count + table_obj.get_aggregate_mentions_count()

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

        #Select the parent of the text content 
        #keep the xpath with the text and the table
        """text_elements = root.xpath("/html/body//span/text()")
        for text_element in text_elements:
            #create document
            text_element_parent = text_element.getparent()
            doc_id = self.get_path(text_element_parent, root)#.base_url()#tree.getpath(text_element)
            doc_content = text_element_parent.text_content()

            print (doc_id)
            print (doc_content)"""


        #f = cStringIO.StringIO('<foo><bar><x1>hello</x1><x1>world</x1></bar></foo>')
        #tree = lxml.etree.parse(f)
        #find_text = etree.XPath("//text()") "//text()/.." ==> get parent directly 

        # and print out the required data
        #print [tree.getpath( text.getparent()) for text in find_text(tree)]
        
        #get the text content of the non-nested <p> items and <li>

        paragraphs = root.xpath('//p[not(.//p)]')
        elem_text_content = []
        for paragraph in paragraphs:
            #print(paragraph.text_content())
            elem_text_content.append(paragraph.text_content())
        
        list_items = root.xpath('//li')
        for item in list_items:
            #print(item.text_content())
            elem_text_content.append(item.text_content())


        self.content =  elem_text_content # root.text_content()


    def get_path(self, element, root):
        path =[]

        while root != element:
            parent = element.getparent()
            indx = parent.index(element)
            path.append(parent.tag+"["+str(indx)+"]")
            element = parent

        return "".join(path)
    def create_documents(self):
                #create documents of text and related tables
        if self.content:
            documents = self.process_text_to_documents(self.content)
        else:
            documents = []
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
        if len(self.tables) <=0:
            print("No Tables")
            return []
        if not text:
            print("Empty Text")
            return []
        text_blocks = text # the text is now splitted by the paragraphs and the list itemsre.split(r'(?:[\.\;](?:\n|\r\n|\r)|(?:\n|\r\n|\r){2,})',text)
        doc_id = self.index
        docs =[]
        #check on a single \n ommit all the lists!
        for block in text_blocks:
            block = re.sub('\s{2,}',' ', block.strip())
            if block is '' or not self.has_number(block):
                continue
            if len(block)< 100: # or len(block)>1000:
                continue
            # if self.count_char(block,'\n') > 4:
            #     continue # most likely it is a list
            #block = re.sub(r'\r\n|\n',' ', block)
            #print(block)
            mentions = extract_mentions_from_text(block)
            #print("document_mentions", mentions)

            # if len(mentions)<1:
            #     continue
            doc_id = doc_id +1
            print("Document Created")
            document = Document(0, doc_id, block)
            document.add_mentions(mentions)
            self.mentions_count = self.mentions_count + len(mentions)

            document_tokens = get_word_set(block)
            cand_tables=[]
            for table in self.tables:
                overlap_coef = get_tokens_overlap(document_tokens, table.general_context_tokens)
                #print("table document overlap coef = %s"%overlap_coef)
                if overlap_coef >= 0.2:
                    print("Candidate Table added")
                    cand_tables.append((table, overlap_coef))
            #only select top 10 candidates using the overlap coefficient to sort 
            # it is very unlikely that a short text will be related to 10 tables!
            cand_tables.sort(key = lambda x: x[1], reverse = True)
            #print(cand_tables)
            cand_tables = cand_tables[: min(5, len(cand_tables))]
            #print(cand_tables)
            cand_tables = [table[0] for table in cand_tables]
            #print(cand_tables)
            document.add_tables(cand_tables)
            docs.append(document)
        return docs

    def get_html_with_annotations(self):
        try:
            root = html.document_fromstring(self.html_content)
        except(Exception) as error:
            print(error)
            return
        cand_elements =[]
        paragraphs = root.xpath('//p[not(.//p)]')
        cand_elements.extend(paragraphs)
        list_items = root.xpath('//li')
        cand_elements.extend(list_items)
        cand_tables = root.xpath('//table[not(.//table)]')

        for document in self.documents:
            doc_text, related_tables = document.get_text_with_mentions_mark_sentences()
            #get the document content 
            #start_text = document.text[:min(20, len(document.text))]
            #find the html element with the text 
            #//id[starts-with(text(),'Annotaions')]
            target_element = self.find_target_element(cand_elements, document)
            if target_element  is None:
                #print(document.text)
                continue

            new_doc_element = self.create_document_element(target_element, doc_text)
            #print(html.tostring(target_element))
            parent_element = target_element.getparent()
            if not parent_element:
                continue
            parent_element.replace(target_element, new_doc_element)
            #target_element.text = doc_text

        for table in self.tables:
            new_table = self.create_table_element(table)
            table_element = self.find_table(cand_tables, new_table)
            if table_element is None:
                print(table.html)
            table_parent = table_element.getparent()
            #table_index = table_parent.index(table_element)
            
            table_parent.replace(table_element, new_table)
                # remove the scripts from the page content
        scripts = root.xpath('//script')
        if scripts:
            for script in scripts:
                script.getparent().remove(script)
        
        styles = root.xpath('//style')
        if styles:
            for style in styles:
                style.getparent().remove(style)
        
        links = root.xpath('//link')  
        if links:
            for link in links:
                link.getparent().remove(link)

        content =  html.tostring(root.xpath('./body')[0], method="html", encoding="UTF-8", pretty_print= False).decode('UTF-8')
        content = content.replace('<body','<div')
        content = content.replace('</body>', '</div>')

        return content

    def create_document_element(self, target_element, document_text):
        new_doc_element = html.fragment_fromstring(document_text, create_parent =target_element.tag)
        return new_doc_element

    def create_table_element(self, table):
        html_element = html.fragment_fromstring(table.get_table_content(), create_parent ='div')
        html_element.set("class","hidden")
        html_element.set("id", "doc-table-"+str(table.table_num))
        table_div = html_element.xpath("./div")[0]
        table_div.set("class", "popover-body")

        #<div id="doc-table" class="table-part">
        html_table =  table_div.xpath("./table")[0]
        #add id to the table as well as to the cells 
        html_table.set("id",  "tbl_"+ str(table.table_num))
        #html_table.set("class", "popover-body")
        cells = html_table.xpath(".//th|.//td")
        cells_count = 1
        header_count = -1
        for cell in cells:
            if cell.tag == 'td':
                indx = cells_count
                cells_count +=1
            else:
                indx = header_count
                header_count -= 1

            cell.set("id" , "c_"+ str(table.table_num)+"." + str(indx))

        return html_element

    def find_target_element(self, cand_elements, document):
        for cand in cand_elements:
            if re.sub('\s{2,}',' ', cand.text_content().strip()) == document.text:
                return cand
        return None 

    def find_table(self, cand_tables, target_table):
        table_content = re.sub('\s{2,}',',', target_table.text_content().strip())
        #print(table_content)
        for cand_table in cand_tables:
            cand_table_content = re.sub('\s{2,}',',', cand_table.text_content().strip()) 
            #print(cand_table_content)
            if  cand_table_content in table_content:
                return cand_table
        return None 


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
    def get_tables_count(self):
        return len(self.tables)
    def get_mentions_count(self):
        return self.mentions_count

    def get_avg_row_count(self):
        if len(self.tables) > 0:
            return self.row_count#/len(self.tables)
        else:
            return 0

    def get_avg_col_count(self):
        if len(self.tables) > 0:
            return self.col_count#/len(self.tables)
        else:
            return 0

    def get_avg_qcell_count(self):
        if len(self.tables) > 0:
            return self.qcell_count#/len(self.tables)
        else:
            return 0

    def get_avg_vcell_count(self):
        if len(self.tables) > 0:
            return self.vcell_count#/len(self.tables)
        else:
            return 0


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
