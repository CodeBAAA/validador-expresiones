# -*- coding: utf-8 -*-
"""
Mini-lenguaje en Python para validar y evaluar expresiones aritméticas con la gramática:

    E -> T ((+|-) T)*
    T -> F ((*|/) F)*
    F -> N | '(' E ')'

Incluye:
- Validación léxica
- Validación sintáctica
- Evaluación según la misma gramática
"""

# ==============================
#  Excepciones
# ==============================

class ParserError(Exception):
    def __init__(self, message, position=None):
        super().__init__(message)
        self.message = message
        self.position = position


# ==============================
#  TOKEN
# ==============================

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


# ==============================
#  LÉXICO
# ==============================

def tokenize(expr):
    expr = expr.strip()

    allowed = set("0123456789+-*/() ")
    for ch in expr:
        if ch not in allowed:
            raise ParserError(f"Símbolo no permitido: '{ch}'")

    tokens = []
    i = 0

    while i < len(expr):
        ch = expr[i]

        # Ignorar espacios
        if ch.isspace():
            i += 1
            continue

        # === NÚMEROS (con validación de ceros a la izquierda) ===
        if ch.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1

            num = expr[i:j]

            # ❗ Regla: NO permitir ceros a la izquierda
            if len(num) > 1 and num[0] == "0":
                raise ParserError(
                    f"Números con ceros a la izquierda no están permitidos: '{num}'"
                )

            tokens.append(Token("NUMBER", num))
            i = j
            continue

        # === OPERADORES Y PARÉNTESIS ===
        if ch in "+-*/()":
            TOK = {
                "+": "PLUS",
                "-": "MINUS",
                "*": "MUL",
                "/": "DIV",
                "(": "LPAREN",
                ")": "RPAREN"
            }
            tokens.append(Token(TOK[ch], ch))
            i += 1
            continue

        raise ParserError(f"Símbolo no permitido: '{ch}'")

    # === BALANCE DE PARÉNTESIS ===
    balance = 0
    for t in tokens:
        if t.type == "LPAREN":
            balance += 1
        elif t.type == "RPAREN":
            balance -= 1
            if balance < 0:
                raise ParserError("Paréntesis de cierre sin apertura previa")

    if balance != 0:
        raise ParserError("Paréntesis no balanceados")

    return tokens


# ==============================
#  PARSER + EVALUACIÓN
# ==============================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, kinds):
        tok = self.current()
        if tok and tok.type in kinds:
            self.pos += 1
            return tok

        expected = " o ".join(kinds)
        got = tok.type if tok else "FIN"
        raise ParserError(f"Se esperaba {expected}, se encontró {got}")

    def parse(self):
        if not self.tokens:
            raise ParserError("Expresión vacía")

        if self.tokens[0].type in ("PLUS", "MINUS", "MUL", "DIV"):
            raise ParserError("La expresión no puede iniciar con un operador")

        result = self.expr()

        if self.current() is not None:
            raise ParserError("Tokens extra después de la expresión")

        if self.tokens[-1].type in ("PLUS", "MINUS", "MUL", "DIV"):
            raise ParserError("La expresión no puede terminar con un operador")

        return result

    # === GRAMÁTICA ===

    def expr(self):
        """E -> T ((+|-) T)*"""
        value = self.term()
        while self.current() and self.current().type in ("PLUS", "MINUS"):
            op = self.current().type
            self.eat((op,))
            right = self.term()
            value = value + right if op == "PLUS" else value - right
        return value

    def term(self):
        """T -> F ((*|/) F)*"""
        value = self.factor()
        while self.current() and self.current().type in ("MUL", "DIV"):
            op = self.current().type
            self.eat((op,))
            right = self.factor()

            if op == "MUL":
                value *= right
            else:
                if right == 0:
                    raise ParserError("División entre 0 no permitida")
                value /= right

        return value

    def factor(self):
        """F -> NUMBER | '(' E ')'"""
        tok = self.current()
        if tok is None:
            raise ParserError("Factor incompleto")

        if tok.type == "NUMBER":
            self.eat(("NUMBER",))
            return float(tok.value)

        if tok.type == "LPAREN":
            self.eat(("LPAREN",))
            val = self.expr()
            self.eat(("RPAREN",))
            return val

        raise ParserError("Se esperaba número o '('")


# ==============================
# VALIDACIÓN SIMPLE
# ==============================

def validate_expression(expr):
    try:
        tokens = tokenize(expr)
        Parser(tokens).parse()
        return True, None
    except ParserError as e:
        return False, e.message


# ==============================
# VALIDAR + EVALUAR
# ==============================

def evaluate_expression(expr):
    try:
        tokens = tokenize(expr)
        result = Parser(tokens).parse()
        return True, None, result
    except ParserError as e:
        return False, e.message, None


# ==============================
# VISTAS
# ==============================

VALID_EXPRESSIONS = []
INVALID_EXPRESSIONS = []

def probar_lista_expresiones(lista):
    for expr in lista:
        ok, msg = validate_expression(expr)
        if ok:
            VALID_EXPRESSIONS.append(expr)
        else:
            INVALID_EXPRESSIONS.append((expr, msg))
