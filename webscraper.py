import argparse
import sys

from html.parser import HTMLParser
from urllib.request import urlopen
from os.path import isfile


class Engine(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.alowed_tags = ['title', 'p']
        self.recording = 0
        self.data = []

    def handle_starttag(self, tag, attributes):
        if tag not in self.alowed_tags:
            return
        if self.recording:
            self.recording += 1
            return
        self.recording = 1

    def handle_endtag(self, tag):
        if tag in self.alowed_tags and self.recording:
          self.recording -= 1

    def handle_data(self, data):
        if self.recording:
            self.data.append(data.strip())
        return self.data


def get_parser():
    """ Разбираем аргументы командной строки """
    parser = argparse.ArgumentParser(
        description='Утилита преобразования html-разметки в обычный текст')
    parser.add_argument('input', nargs='?', default=None,
                        help="URL ресурса для преобразования.")
    parser.add_argument('-o', '--output', type=str,
                        help='Вывод в файл (по умолчанию: stdout).')
    parser.add_argument('-e', '--encoding', type=str,
                        help='Кодировка содержимого (по умолчанию: utf-8)', default='utf-8')
    return parser


def translate(source_data):

    source_data = source_data.strip()
    if not source_data:
        return ""

    parser = Engine()
    parser.feed(source_data)

    return ' '.join(parser.data)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if args.input.startswith("http://") or args.input.startswith("https://"):
        source_data = urlopen(args.input).read().decode(args.encoding)
    else:
        print("Ошибка: Заданный ресурс недоступен '{}'.\n".format(args.input))
        parser.print_help()
        sys.exit(-1)

    result = translate(source_data)

    text = result
    if args.output:
        with open(args.output, 'w') as open_file:
            open_file.write(text)
    else:
        print(text)
