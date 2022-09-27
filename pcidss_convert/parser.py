import mammoth
import xml.etree.ElementTree as ET
import re
import logging
import string

class DocxParser:
    symbols = string.ascii_lowercase;

    def __init__(self, docx_path, table_hotword):
        self.path = docx_path
        self.table_hotword = table_hotword
        try:
            with open(self.path, 'rb') as docx_file:
                result = mammoth.convert_to_html(docx_file)
        except:
            logging.warn('Cannot open DocX src file: {}'.format(self.path))
            raise
        self.html = str('<html>' + result.value + '</html>').encode('utf-8')
        self.data = []
        self.previous_row_data = None
        self.current_rowspan = 0
        self.id = 0
        self.text_regexp = re.compile(r'^\([a-z]\)[\s,\t]+')
        self.skip_next_row = False
        self.child_count = 0

    def _skip_next_row(self):
        self.skip_next_row = True

    def _is_skipped(self):
        if self.skip_next_row:
            self.skip_next_row = False
            return True
        return False

    def _fill_data(self, data, row, shift_cell):
        self.id += 1
        if shift_cell:
            text_element = row[0]
            testing_element = row[1]
        else:
            text_element = row[1]
            testing_element = row[2]
        if text_element.get('rowspan') > 1:
            self._skip_next_row()
        data['id'] = self.id
        data['text'] = str(re.sub(self.text_regexp, '', " ".join(["".join(element.itertext()) for element in text_element])))
        data['milestone'] = '';
        data['section'] = '';
        data['req'] = int(data['code'].split('.')[0]);
        if len(testing_element):
            data['testing'] = '<ul><li>' + '</li><li>'.join(["".join(element.itertext()) for element in testing_element]) + '</li></ul>'
            data['answer_type'] = 'YES_NO'
        else:
            data['testing'] = ''
            data['answer_type'] = 'NONE'

    def _extract_data(self, row):
        template = '{}.{}'
        data = {}
        shift_cell = False
        code = ""
        try:
            rowspan = int(row[0].get('rowspan'))
        except:
            rowspan = 0
        if self.current_rowspan == 0:
            code = str("".join(row[0].itertext())).replace(" ", "")
        else:
            shift_cell = True
        if not len(code):
            if self.child_count == 0:
                self.base_code = self.previous_row_data['code']
                self.previous_row_data['code'] = template.format(self.base_code, self.symbols[0])
            self.child_count += 1
            code = template.format(self.base_code, self.symbols[self.child_count])
        else:
            self.child_count = 0
        data['code'] = code
        self._fill_data(data, row, shift_cell)
        if self.current_rowspan > 0:
            self.current_rowspan -= 1
        elif rowspan > 1:
            self.current_rowspan = rowspan - 1
        self.previous_row_data = data
        return data

    def extract(self):
        root = ET.fromstring(self.html)
        tables = root.findall('.//table/tr/td/p[strong="'+ self.table_hotword +'"]/../../..')
        return [self._extract_data(table[index]) for table in tables for index in range(2, len(table)) if not self._is_skipped()]
