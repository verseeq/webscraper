import argparse
import sys
import os
import os.path
import errno

from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import urlsplit
from os.path import isfile


class Engine(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.alowed_tags = ['title', 'p']
        self.recording = 0
        self.data = []

    def handle_starttag(self, tag, attributes):
        if tag not in self.alowed_tags:
            if self.recording:
                if tag == 'a':
                    links = []
                    for name, value in attributes:
                        if name == "href":
                            links.append('[{}]'.format(value))
                    self.data.append(' '.join(links))
            return
        if self.recording:
            self.recording += 1
            return
        self.recording = 1

    def handle_endtag(self, tag):
        if tag in self.alowed_tags and self.recording:
            self.recording -= 1
        if tag in self.alowed_tags and self.recording == 0:
            self.data.append('\n\n')

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)
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

    return ''.join(parser.data)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    if args.input.startswith("http://") or args.input.startswith("https://"):
        source_data = urlopen(args.input).read().decode(
            args.encoding, "replace")
    else:
        print("Ошибка: Заданный ресурс недоступен '{}'.\n".format(args.input))
        parser.print_help()
        sys.exit(-1)

    result = translate(source_data)

    text = result
    if args.output:
        with open(args.output, encoding='utf-8', mode='w') as open_file:
            open_file.write(text)
    else:
        o = urlsplit(args.input)
        path = './{}{}'.format(o.netloc, o.path)
        if os.path.basename(path) != '':
            filename = os.path.splitext(path)[0] + '.txt'
        else:
            filename = path.rsplit('/', 1)[0] + '.txt'

        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        with open(filename, encoding='utf-8', mode='w') as open_file:
            open_file.write(text)
