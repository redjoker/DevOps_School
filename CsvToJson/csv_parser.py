# Import system library
import sys


# Main function
def main(filename):
    file_contents = open(filename, "r").read()
    c = CSVParser(",")
    print(c.parse_file(file_contents))


# Exception for parsing CSV file
class CSVParseException(Exception):
    def __init__(self, msg, linenum, linestart, pos, str):
        self.msg = msg
        self.linenum = linenum
        self.linestart = linestart
        self.pos = pos
        self.str = str

    def __str__(self):
        text = "\nParse exception on line {}".format(self.linenum + 1)
        text += "\n"
        text += self.msg
        text += "\n"
        elpos = self.pos
        while elpos < len(self.str) and self.str[elpos] != "\n":
            elpos += 1
        if elpos == len(self.str):
            self.str += "<EOF>"
            elpos += 5
        text += self.str[self.linestart:elpos]
        text += "\n"
        text += "-" * (self.pos - self.linestart) + "^"
        text += "\n"
        return text


class CSVParser(object):

    def __init__(self, separator, quote='"', escape_char='"'):
        self.separator = separator
        self.quote = quote
        self.escape_char = escape_char
        self.str = ""
        self.linenum = 0
        self.linestart = 0

    def parse_file(self, str):
        rows = []
        self.str = str
        pos = 0
        while True:
            if pos >= len(self.str):
                return rows
            else:
                pos, row = self.__parse_first_cell_of_row(pos)
                rows.append(row)
                self.linestart = pos
                self.linenum += 1

    def __parse_potential_quote_character(self, pos):
        if pos >= len(self.str):
            raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                    self.linenum, self.linestart, pos, self.str)
        elif self.str[pos] == self.separator or self.str[pos] == "\n":
            return pos, ""
        elif self.str[pos] == self.quote:
            pos, text = self.__parse_quoted_cell(pos + 1)
            return pos, self.quote + text
        else:
            return pos, ""

    def __parse_quoted_cell(self, pos):
        text = ""
        while True:
            if pos >= len(self.str):
                raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                        self.linenum, self.linestart, pos, self.str)
            elif self.str[pos] == self.quote and self.escape_char != self.quote:
                return pos + 1, text
            elif self.str[pos] == self.quote:
                pos, outer_text = self.__parse_potential_quote_character(pos + 1)
                return pos, text + outer_text
            elif self.str[pos] == self.escape_char:
                pos += 1
            else:
                text += self.str[pos]
                pos += 1

    def __parse_first_char_of_cell(self, pos):
        if pos >= len(self.str):
            raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                    self.linenum, self.linestart, pos, self.str)
        elif self.str[pos] == self.quote:
            return self.__parse_quoted_cell(pos + 1)
        else:
            return self.__parse_non_quoted_cell(pos)

    def __parse_non_quoted_cell(self, pos):
        text = ""
        while True:
            if pos >= len(self.str):
                raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                        self.linenum, self.linestart, pos, self.str)
            elif self.str[pos] == self.quote:
                raise CSVParseException(
                    "Unexpected '{}': we should not see quote characters in a non-quoted cell".format(self.quote),
                    self.linenum, self.linestart, pos, self.str)
            elif self.str[pos] == self.separator or self.str[pos] == "\n":
                return pos, text
            else:
                text += self.str[pos]
                pos += 1

    def __parse_first_cell_of_row(self, pos):
        if pos >= len(self.str):
            raise CSVParseException("Empty file", self.linenum, self.linestart, pos, self.str)
        if self.str[pos] == "\n":
            return pos + 1, []

        pos, text = self.__parse_first_char_of_cell(pos)
        pos, row = self.__parse_row(pos)
        row = [text] + row
        return pos, row

    def __parse_row(self, pos):
        cells = []
        while True:
            if pos >= len(self.str):
                raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                        self.linenum, self.linestart, pos, self.str)
            elif self.str[pos] == "\n":
                return pos + 1, cells
            elif self.str[pos] == self.separator:
                pos, cell = self.__parse_first_char_of_cell(pos + 1)
                cells.append(cell)
            else:
                raise CSVParseException("Unexpected character, expected separator, got '{}'".format(self.str[pos]),
                                        self.linenum, self.linestart, pos, self.str)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("USAGE: {} <filename_to_read.csv>".format(sys.argv[0]))
        sys.exit(-1)
    main(sys.argv[1])
