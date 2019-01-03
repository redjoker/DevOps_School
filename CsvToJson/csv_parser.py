# Import system library
import sys


# Main function
def main(filename):
    # Read entire file
    file_contents = open(filename, "r").read()
    # Make parser for CSV files
    c = CSVParser(",")
    # Print parsed files
    print(c.parse_file(file_contents))


# Exception for parsing CSV file
class CSVParseException(Exception):
    # Constructor
    def __init__(self, msg, linenum, linestart, pos, str):
        # Exception message
        self.msg = msg
        # Line number of CSV file
        self.linenum = linenum
        # Line starting position within read CSV file
        self.linestart = linestart
        self.pos = pos
        self.str = str

    # String method override
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

    # Constructor with default quote and escape character "
    def __init__(self, separator, quote='"', escape_char='"'):
        # Separator
        self.separator = separator
        # Quote character
        self.quote = quote
        # Escape quote character
        self.escape_char = escape_char
        # CSV file contents
        self.str = ""
        # Line number of CSV
        self.linenum = 0
        # CSV line starting index in read string
        self.linestart = 0

    # Parser method
    def parse_file(self, str):
        # CSV rows read into array
        rows = []
        # CSV contents read into string
        self.str = str
        # Current position of parser
        pos = 0
        # Loop through CSV contents
        while True:
            # End of content
            if pos >= len(self.str):
                return rows
            # Content
            else:
                # Start parsing first cell of row, return position in line of read CSV file and the parsed row
                pos, row = self.__parse_first_cell_of_row(pos)
                # Append parsed row to array
                rows.append(row)
                # Update starting point of next line in CSV file
                self.linestart = pos
                # Update line number of CSV to parse
                self.linenum += 1

    def __parse_potential_quote_character(self, pos):
        if pos >= len(self.str):
            raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                    self.linenum, self.linestart, pos, self.str)
        # Don't add separator or newline characters to parsed text
        elif self.str[pos] == self.separator or self.str[pos] == "\n":
            return pos, ""
        # Parse cell as quoted cell
        elif self.str[pos] == self.quote:
            pos, text = self.__parse_quoted_cell(pos + 1)
            return pos, self.quote + text
        # Actual quote, don't add to parsed text
        else:
            return pos, ""

    # Parse quoted cell
    def __parse_quoted_cell(self, pos):
        # String to hold contents of cell
        text = ""
        # Loop through string
        while True:
            # Unexpected EOF exception
            if pos >= len(self.str):
                raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                        self.linenum, self.linestart, pos, self.str)
            # Encounter next quote character (different from escape quote character)
            # Return next position in string and the parsed cell text

            elif self.str[pos] == self.quote and self.escape_char != self.quote:
                return pos + 1, text

            # Encounter next quote character
            # Evaluate whether next position is a quote character or escape character
            # Return position in string and the parsed cell text concatenated with the outside text

            elif self.str[pos] == self.quote:
                pos, outer_text = self.__parse_potential_quote_character(pos + 1)
                return pos, text + outer_text

            # Encounter escape quote character (different from quote character), skip to next position
            elif self.str[pos] == self.escape_char:
                pos += 1

            # Encounter regular text, add to parsed text and move to next position
            else:
                text += self.str[pos]
                pos += 1

    # Parse first character of cell
    def __parse_first_char_of_cell(self, pos):
        # Unexpected end fo file exception
        if pos >= len(self.str):
            raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                    self.linenum, self.linestart, pos, self.str)
        # Parse quoted cell at next position
        elif self.str[pos] == self.quote:
            return self.__parse_quoted_cell(pos + 1)
        # Parse nonquoted cell at next position
        else:
            return self.__parse_non_quoted_cell(pos)

    # Parse regular cell
    def __parse_non_quoted_cell(self, pos):
        text = ""
        while True:
            # Unexpected EOF exception
            if pos >= len(self.str):
                raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                        self.linenum, self.linestart, pos, self.str)

            # Unexpected quote exception
            elif self.str[pos] == self.quote:
                raise CSVParseException(
                    "Unexpected '{}': we should not see quote characters in a non-quoted cell".format(self.quote),
                    self.linenum, self.linestart, pos, self.str)

            # End of cell or line, return string position and parsed text
            elif self.str[pos] == self.separator or self.str[pos] == "\n":
                return pos, text

            # Add character to parsed text and move to next position
            else:
                text += self.str[pos]
                pos += 1

    # Parse first cell of row
    def __parse_first_cell_of_row(self, pos):
        # Throw exception for empty file
        if pos >= len(self.str):
            raise CSVParseException("Empty file", self.linenum, self.linestart, pos, self.str)
        # Newline encountered, return next position in string and empty array
        if self.str[pos] == "\n":
            return pos + 1, []

        # Return next position in string and parse text of first character of cell
        pos, text = self.__parse_first_char_of_cell(pos)
        # Parse row and return position of next row and the current row as an array
        pos, row = self.__parse_row(pos)
        # Add parsed text of first character of cell and remainder of row's cells to array
        row = [text] + row
        # Return current position and parsed cells of row
        return pos, row

    # Parse row
    def __parse_row(self, pos):
        # Current row as array
        cells = []
        # Loop through row
        while True:
            # Unexpected EOF exception
            if pos >= len(self.str):
                raise CSVParseException("Unexpected end of file during row parse. All rows must end in a newline.",
                                        self.linenum, self.linestart, pos, self.str)
            # End of line, return next position and parsed cells
            elif self.str[pos] == "\n":
                return pos + 1, cells
            # Encounter separator
            elif self.str[pos] == self.separator:
                # Parse first character of next cell and return position and cell
                pos, cell = self.__parse_first_char_of_cell(pos + 1)
                # Append cell to array of parsed cells for row
                cells.append(cell)

            # Unexpected separator exception
            else:
                raise CSVParseException("Unexpected character, expected separator, got '{}'".format(self.str[pos]),
                                        self.linenum, self.linestart, pos, self.str)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("USAGE: {} <filename_to_read.csv>".format(sys.argv[0]))
        sys.exit(-1)
    main(sys.argv[1])
