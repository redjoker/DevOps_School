# Import system library
import sys

DIGIT_START_CHARACTERS = set("-0123456789")
ESCAPABLE_CHARS = set("\"\\/bfnrtu")
HEX_DIGITS = set("0123456789abcdefABCDEF")
HD = "0123456789abcdef"
VALUE_START_CHARS = "\"-0123456789[{tfn"


# Main function
def main(filename):
    # Read entire file
    file_contents = open(filename, "r").read()
    # Make parser for JSON files
    j = JSONParser()
    # Print parsed files
    print(j.parse_file(file_contents))


# Exception for parsing JSON file
class JSONParseException(Exception):
    # Constructor
    def __init__(self, msg, linenum, linestart, pos, str):
        # Exception message
        self.msg = msg
        # Line number of JSON file
        self.linenum = linenum
        # Line starting position within read JSON file
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


class JSONParser(object):

    # Constructor with default quote and escape character "
    def __init__(self):
        # JSON file contents
        self.str = ""
        # Line number of JSON
        self.linenum = 0
        # JSON line starting index in read string
        self.linestart = 0

    def __parse_literal(self, pos, literal):
        if len(literal) == 0:
            return pos, True

        elif len(self.str[pos:]) < len(literal):
            raise JSONParseException("Unexpected end of file",
                                     self.linenum,
                                     self.linestart,
                                     len(self.str[pos:]) + pos,
                                     self.str)

        elif self.str[pos] != literal[0]:
            raise JSONParseException("Unexpected character, expected \"{}\", got \"{}\"".format(literal[0],
                                                                                                self.str[pos]),
                                     self.linenum,
                                     self.linestart,
                                     pos,
                                     self.str)

        return self.__parse_literal(pos + 1, literal[1:])

    def parse_true(self, pos):
        return self.__parse_literal(pos, "true")

    def parse_false(self, pos):
        pos, val = self.__parse_literal(pos, "false")
        return pos, not val

    def parse_null(self, pos):
        pos, val = self.__parse_literal(pos, "null")
        return pos, None

    def clear_whitespace(self, pos):
        while pos < len(self.str) and self.str[pos] in " \t\n\r":
            if self.str[pos] == "\n":
                self.linenum += 1
                self.linestart = pos + 1
            pos += 1

        if pos >= len(self.str):
            raise JSONParseException("Unexpected end of file",
                                     self.linenum,
                                     self.linestart,
                                     len(self.str[pos:]) + pos,
                                     self.str)

        return pos

    def parse_array(self, pos):
        if self.str[pos] != "[":
            raise JSONParseException("Invalid array",
                                     self.linenum,
                                     self.linestart,
                                     pos,
                                     self.str)

        pos = self.clear_whitespace(pos + 1)

        vals = []
        while self.str[pos] != "]":
            pos, val = self.parse_value(pos)
            vals.append(val)

            pos = self.clear_whitespace(pos)

            if self.str[pos] not in ",]":
                raise JSONParseException("Unexpected character, expected \",\" or \"]\", got \"{}\"".format(
                    self.str[pos]),
                    self.linenum,
                    self.linestart,
                    pos,
                    self.str)

            if self.str[pos] == ",":
                pos += 1

        return pos + 1, vals

    def __parse_string_literal(self, pos):
        if pos >= len(self.str):
            raise JSONParseException("Unexpected end of file",
                                     self.linenum,
                                     self.linestart,
                                     pos,
                                     self.str)
        if self.str[pos] in ESCAPABLE_CHARS:
            if self.str[pos] == "\"":
                return pos + 1, "\""

            if self.str[pos] == "\\":
                return pos + 1, "\\"

            if self.str[pos] == "/":
                return pos + 1, "/"

            if self.str[pos] == "b":
                return pos + 1, "\b"

            if self.str[pos] == "f":
                return pos + 1, "\f"

            if self.str[pos] == "n":
                return pos + 1, "\n"

            if self.str[pos] == "r":
                return pos + 1, "\r"

            if self.str[pos] == "t":
                return pos + 1, "\t"

            if self.str[pos] == "u":
                if len(self.str[pos:]) < 5:
                    raise JSONParseException("Unexpected end of file",
                                             self.linenum,
                                             self.linestart,
                                             pos,
                                             self.str)

                hexstring = self.str[pos + 1: pos + 5]
                i = 1
                num = 0

                for char in hexstring:
                    num *= 16
                    if char not in HEX_DIGITS:
                        raise JSONParseException("Invalid Unicode hex string",
                                                 self.linenum,
                                                 self.linestart,
                                                 pos + i,
                                                 str)
                    num += HD.index(char.lower())
                    i += 1

                return pos + 5, chr(num)

        else:
            raise JSONParseException("Unexpected character in escape sequence",
                                     self.linenum,
                                     self.linestart,
                                     pos,
                                     self.str)

    def parse_string(self, pos):
        if self.str[pos] != "\"":
            raise JSONParseException("Invalid string",
                                     self.linenum,
                                     self.linestart,
                                     pos,
                                     self.str)

        text = ""
        pos += 1

        while True:
            if pos >= len(self.str):
                raise JSONParseException("Unexpected end of file",
                                         self.linenum,
                                         self.linestart,
                                         pos,
                                         self.str)

            if self.str[pos] == "\"":
                return pos + 1, text

            elif self.str[pos] == "\\":
                pos, string_literal = self.__parse_string_literal(pos + 1)
                text += string_literal

            else:
                text += self.str[pos]
                pos += 1

    def parse_object(self, pos):
        if self.str[pos] != "{":
            raise JSONParseException("Invalid object",
                                     self.linenum,
                                     self.linestart,
                                     pos,
                                     self.str)
        obj = {}
        pos += 1
        key = ""
        value = None

        while self.str[pos] != "}":
            self.clear_whitespace(pos)

            if pos >= len(self.str):
                raise JSONParseException("Unexpected end of file",
                                         self.linenum,
                                         self.linestart,
                                         pos,
                                         self.str)

            if self.str[pos] == "\"":
                pos, key = self.parse_string(pos)

            elif self.str[pos] in ":\t\n\r ":
                pos += 1

            elif self.str[pos] in VALUE_START_CHARS:
                pos, value = self.parse_value(pos)

            elif self.str[pos] == ",":
                obj[key] = value
                key == ""
                value = None

            elif self.str[pos] == "}":
                obj[key] = value
                return pos, obj



    def parse_value(self, pos):
        pos = self.clear_whitespace(pos)

        chr = self.str[pos]

        if chr == "[":
            return self.parse_array(pos)

        elif chr == "{":
            return self.parse_object(pos)

        elif chr in DIGIT_START_CHARACTERS:
            return self.parse_number(pos)

        elif chr == "\"":
            return self.parse_string(pos)

        elif chr == "t":
            return self.parse_true(pos)

        elif chr == "f":
            return self.parse_false(pos)

        elif chr == "n":
            return self.parse_null(pos)

        else:
            raise JSONParseException("Invalid value",
                                     self.linenum,
                                     self.linestart,
                                     pos,
                                     self.str)


if __name__ == "__main__":
    j = JSONParser()
    j.str = "{\"Hello \\\"World\\\": true,\"Normal string\": true}"
    print(j.parse_value(0))

    #j = JSONParser()
    #j.str = "["
    #print(j.parse_value(0))

    # if len(sys.argv) != 2:
    #    print("USAGE: {} <filename_to_read.json>".format(sys.argv[0]))
    #    sys.exit(-1)
    # main(sys.argv[1])
