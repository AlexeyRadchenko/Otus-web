import xlwt
from django.db.models import Q

from .formats_io import ExcelUnloadFormat
from counters.models import Counters, Accounts
from django.core.cache import cache
from django.conf import settings


class FileWriter:
    extensions = {
        1: '.xls',
        2: '.xlsx',
    }

    def __init__(self, file_extension):
        self.file_type = file_extension
        self.result = {}
        self.writers_selector = {
            1: self.xls_writer,
            2: self.xlsx_writer,
        }
        self.row_format_selector = {
            'xls': ExcelUnloadFormat,
            'xlsx': ExcelUnloadFormat,
        }

    @staticmethod
    def xls_write_rows(writer, rows, style=None):
        for i, column in enumerate(rows):
            writer.write(0, i, column[0], style)
            writer.col(i).width = column[1]

    def xls_writer(self):
        book = xlwt.Workbook()
        sheet = book.add_sheet('TDSheet', cell_overwrite_ok=True)
        self.xls_write_rows(sheet, ExcelUnloadFormat.header, xlwt.easyxf(ExcelUnloadFormat.header_style))
        return book, sheet

    def xlsx_writer(self):
        pass


class DataUnloader(FileWriter):
    default_file_name_select = {
        1: 'все_счетчики',
        2: 'энергосчетчики',
        3: 'водосчетчики',
        4: 'газовые_счетчики',
    }

    def __init__(
            self,
            file_extension,
            process_id,
            month,
            year,
            file_name=None,
            account=None,
            street=None,
            house_number=None,
            apartments=None,
            counters_type=None,
            separated_of_counters_type=False,

    ):
        super().__init__(file_extension)
        self.account = account
        self.street = street
        self.house_number = house_number
        self.apartments = apartments
        self.counters_type = counters_type
        self.separated_of_counters_type = separated_of_counters_type
        self.month = month
        self.year = year
        self.process_id = process_id
        self.file_name = file_name
        self.file_extension = self.extensions[file_extension]
        self.writer = self.writers_selector[file_extension]()
        self.unloader = {
            '.xls': self.xls_unload,
            '.xlsx': self.xlsx_unload,
        }
        self.progress_step = 0
        self.progress = 0

    def get_data_from_db(self):
        counter_type = {
            1: Q(counter_type__contains='Электроэнергия') | Q(counter_type__contains='вода') | Q(
                counter_type__contains='Газ'),
            2: Q(counter_type__contains='Электроэнергия'),
            3: Q(counter_type__contains='вода'),
            4: Q(counter_type__contains='Газ'),
        }
        print(counter_type[self.counters_type])
        counters_objects = Counters.objects.select_related(
            'account_id'
        ).filter(
            counter_type[self.counters_type],
            date_update__year=self.year,
            date_update__month=self.month,
            in_work=True
        ).values(
            'account_id',
            'account_id__name',
            'account_id__street',
            'account_id__house_number',
            'account_id__apartments_number',
            'counter_type',
            'id_out_system',
            'serial_number',
            'counter_data_simple',
            'counter_data_day',
            'counter_data_night',
            'old_counter_data_simple',
            'old_counter_data_day',
            'old_counter_data_night',
            'date_update'
        )

        return counters_objects

    def file_name_generator(self):
        if not self.file_name:
            return f'{self.default_file_name_select[self.counters_type]}_{self.month}-{self.year}{self.file_extension}'
        else:
            return f'{self.file_name}_{self.month}-{self.year}{self.file_extension}'

    def download_url_generator(self, url, file_name):
        if self.progress < 100:
            cache.set(self.process_id, 100)
        url_id = f'url_{self.process_id}'
        cache.set(url_id, (url, file_name,))

    def set_n_update_progress(self):
        self.progress += self.progress_step
        cache.set(self.process_id, round(self.progress))

    def xls_unload(self):
        db_data = self.get_data_from_db()
        self.progress_step = len(db_data) / 100
        book, sheet = self.writer
        for row, data in enumerate(db_data, start=1):
            row_data = ExcelUnloadFormat(row, data).db_data_to_row_data()
            for column, cell_value in enumerate(row_data):
                sheet.write(row, column, cell_value)
                self.set_n_update_progress()
        file_name = self.file_name_generator()
        download_url = f'/media/export/{file_name}'
        book.save(f'{settings.BASE_DIR}{download_url}')
        self.download_url_generator(download_url, file_name)

    def xlsx_unload(self):
        pass

    def unload(self):
        self.unloader[self.file_extension]()
