from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QRegExp
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

class MyFormatter:
    def __init__(self, string_color, comment_color, keyword_color):
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(string_color))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(comment_color))

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(keyword_color))

    def apply_format(self, text, highlighter):
        patterns = [
            (QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), self.string_format),  # Cadenas entre comillas dobles
            (QRegExp(r'//[^\n]*'), self.comment_format)  # Comentarios de línea
        ]

        for pattern, fmt in patterns:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                highlighter.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

class CustomHighlighter(QSyntaxHighlighter):
    def __init__(self, parent, language, formatter):
        super().__init__(parent)
        self.lexer = get_lexer_by_name(language)
        self.formatter = formatter

    def highlightBlock(self, text):
        for token, content in self.lexer.get_tokens(text):
            start = text.find(content)
            length = len(content)
            if token in [Token.Literal.String, Token.Comment.Single, Token.Keyword]:
                if token == Token.Literal.String:
                    self.setFormat(start, length, self.formatter.string_format)
                elif token == Token.Comment.Single:
                    self.setFormat(start, length, self.formatter.comment_format)
                elif token == Token.Keyword:
                    self.setFormat(start, length, self.formatter.keyword_format)
        self.formatter.apply_format(text, self)

def getHighlighter(language):
    if language == "Python":
        return CustomHighlighter(None, "python", MyFormatter("#00ff80", "#586e75", "#ff0000"))  # Verde, Gris, Rojo
    elif language == "HTML":
        return CustomHighlighter(None, "html", MyFormatter("#00ff80", "#586e75", "#ff0000"))
    elif language == "JavaScript":
        return CustomHighlighter(None, "javascript", MyFormatter("#00ff80", "#586e75", "#ff0000"))
    elif language == "SQL":
        return CustomHighlighter(None, "sql", MyFormatter("#00ff80", "#586e75", "#ff0000"))
    elif language == "Bash":
        return CustomHighlighter(None, "bash", MyFormatter("#00ff80", "#586e75", "#ff0000"))
    elif language == "C++":
        return CustomHighlighter(None, "c++", MyFormatter("#00ff80", "#586e75", "#ff0000"))
    elif language == "C":
        return CustomHighlighter(None, "c", MyFormatter("#00ff80", "#586e75", "#ff0000"))
    elif language == "Lua":
        return CustomHighlighter(None, "lua", MyFormatter("#00ff80", "#586e75", "#ff0000"))
    elif language == "SQLite":
        return CustomHighlighter(None, "sqlite", MyFormatter("#00ff80", "#586e75", "#ff0000"))
    else:
        return None
