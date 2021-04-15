import base64
import csv

class CsvData(models.TransientModel):
    name = []
    data = []

    @staticmethod
    def create_from_base64(file_content, delimiter=',', quote_char='"'):
        csv_string_content = base64.b64decode(self.file)
        csv_list_content = csv.reader(csv_string_content.split('\n'), delimiter=delimiter, quotechar=quote_char)
        csv_data = CsvData()
        csv_data.data = csv_list_content
        return csv