# -*- coding: utf-8 -*-
"""
Mini-lenguaje en Python para validar expresiones aritméticas con la gramática:

    E -> T ((+|-) T)*
    T -> F ((*|/) F)*
    F -> N | '(' E ')'
    N -> dígito+

Caracteres permitidos:
    - Dígitos: 0-9
    - Operadores: + - * /
    - Paréntesis: ( )
    - Espacios (se ignoran)

Reglas adicionales:
    - No puede iniciar ni terminar con operador.
    - No operadores consecutivos.
    - No operandos consecutivos sin operador.
    - Paréntesis balanceados y bien anidados.
"""

# ==============================
#  Excepciones y estructura base
# ==============================

class ParserError(Exception):
    """Error de análisis léxico/sintáctico con mensaje descriptivo."""
    def __init__(self, message, position=None):
        super().__init__(message)
        self.message = message
        self.position = position


class Token:
    """Token simple con tipo y valor."""
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


# ==========================
#  Tokenización (léxico)
# ==========================

def tokenize(expr):
    """
    Convierte una cadena de expresión en una lista de tokens.
    También verifica caracteres permitidos y balance de paréntesis.
    """
    expr = expr.strip()

    # Validación léxica básica: sólo caracteres permitidos
    allowed_chars = set("0123456789+-*/() ")
    for ch in expr:
        if ch not in allowed_chars:
            raise ParserError(f"Símbolo no permitido: '{ch}'")

    tokens = []
    i = 0
    while i < len(expr):
        ch = expr[i]

        # Ignorar espacios
        if ch.isspace():
            i += 1
            continue

        # Números (uno o más dígitos)
        if ch.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            num = expr[i:j]
            tokens.append(Token("NUMBER", num))
            i = j
            continue

        # Operadores y paréntesis
        if ch in "+-*/()":
            type_map = {
                '+': "PLUS",
                '-': "MINUS",
                '*': "MUL",
                '/': "DIV",
                '(': "LPAREN",
                ')': "RPAREN"
            }
            tokens.append(Token(type_map[ch], ch))
            i += 1
            continue

        # Por si acaso (no debería llegar aquí por la validación previa)
        raise ParserError(f"Símbolo no permitido: '{ch}'")

    # Verificación de balance de paréntesis usando una "pila" implícita (contador)
    balance = 0
    for t in tokens:
        if t.type == "LPAREN":
            balance += 1
        elif t.type == "RPAREN":
            balance -= 1
            if balance < 0:
                raise ParserError("Paréntesis de cierre sin apertura previa")

    if balance != 0:
        raise ParserError("Paréntesis no balanceados: falta cierre")

    return tokens


# ==========================
#  Parser (sintaxis / gramática)
# ==========================

class Parser:
    """
    Parser recursivo que implementa la gramática:

        E -> T ((+|-) T)*
        T -> F ((*|/) F)*
        F -> NUMBER | '(' E ')'
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        """Devuelve el token actual o None si se terminó la lista."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token_types):
        """
        Consume un token si su tipo está en token_types.
        Si no coincide, lanza ParserError.
        """
        tok = self.current()
        if tok and tok.type in token_types:
            self.pos += 1
            return tok

        expected = " o ".join(token_types)
        got = tok.type if tok else "FIN"
        raise ParserError(f"Se esperaba {expected}, se encontró {got}", position=self.pos)

    def parse(self):
        """
        Punto de entrada del parser.
        Valida reglas globales de inicio/fin y que no haya tokens sobrantes.
        """
        if not self.tokens:
            raise ParserError("Expresión vacía")

        # Regla: no iniciar con operador
        if self.tokens[0].type in ("PLUS", "MINUS", "MUL", "DIV"):
            raise ParserError("La expresión no puede iniciar con un operador")

        # E
        self.expr()

        # No deben quedar tokens sin procesar
        if self.current() is not None:
            raise ParserError("Tokens extra después de una expresión válida", position=self.pos)

        # Regla: no terminar con operador
        if self.tokens and self.tokens[-1].type in ("PLUS", "MINUS", "MUL", "DIV"):
            raise ParserError("La expresión no puede terminar con un operador")

    # ----- No terminales -----
    
        def expr(self):
            """E -> T ((+|-) T)*"""
            value = self.term()
            while self.current() and self.current().type in ("PLUS", "MINUS"):
                op = self.current().type
                self.eat((op,))
                right = self.term()
                if op == "PLUS":
                    value += right
                else:
                    value -= right
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
            if tok.type == "NUMBER":
                self.eat(("NUMBER",))
                return float(tok.value)
    
            if tok.type == "LPAREN":
                self.eat(("LPAREN",))
                value = self.expr()
                self.eat(("RPAREN",))
                return value
    
            raise ParserError("Se esperaba número o '('")



# ==========================
#  Funciones de validación
# ==========================

def validate_expression(expr):
    """
    Valida una expresión completa.

    Devuelve:
        (True, None) si es válida.
        (False, mensaje_error) si es inválida.
    """
    expr_stripped = expr.strip()
    if expr_stripped == "":
        return False, "Expresión vacía"

    try:
        tokens = tokenize(expr_stripped)
        parser = Parser(tokens)
        parser.parse()
        # Si llegamos aquí, la expresión es válida
        return True, None
    except ParserError as e:
        return False, e.message


# ==========================
#  "Vistas": listas de válidos / inválidos
# ==========================

VALID_EXPRESSIONS = []      # vista de expresiones válidas
INVALID_EXPRESSIONS = []    # vista de expresiones inválidas: (expresión, motivo)


def probar_lista_expresiones(expresiones):
    """
    Recorre una lista de expresiones, las valida y las guarda
    en VALID_EXPRESSIONS e INVALID_EXPRESSIONS.
    """
    for expr in expresiones:
        is_valid, msg = validate_expression(expr)
        if is_valid:
            VALID_EXPRESSIONS.append(expr)
            print(f"✅ VÁLIDA  : {expr}")
        else:
            INVALID_EXPRESSIONS.append((expr, msg))
            print(f"❌ INVÁLIDA: {expr}  -> {msg}")


# ==========================
#  Vista previa interactiva (para testear)
# ==========================

def interactive_preview():
    """
    Vista previa por consola para testear el lenguaje.

    - Pides expresiones una por una.
    - El sistema dice si son válidas o no y el motivo.
    - Guarda automáticamente en las vistas:
        - VALID_EXPRESSIONS
        - INVALID_EXPRESSIONS
    """
    print("==============================================")
    print("  Validador de expresiones aritméticas")
    print("  Escribe una expresión o 'salir' para terminar")
    print("==============================================\n")

    while True:
        expr = input("Expresión> ").strip()
        if expr.lower() in ("salir", "exit", "quit"):
            break

        is_valid, msg = validate_expression(expr)
        if is_valid:
            print("   ✅ Expresión VÁLIDA\n")
            VALID_EXPRESSIONS.append(expr)
        else:
            print(f"   ❌ Expresión INVÁLIDA: {msg}\n")
            INVALID_EXPRESSIONS.append((expr, msg))

    # Resumen final
    print("\n========== RESUMEN ==========")
    print("Expresiones válidas:")
    for e in VALID_EXPRESSIONS:
        print("  -", e)

    print("\nExpresiones inválidas:")
    for e, m in INVALID_EXPRESSIONS:
        print(f"  - {e}  -> {m}")
    print("=============================")


# ==========================
#  Pruebas rápidas sugeridas
# ==========================

if __name__ == "__main__":
    # Casos de prueba recomendados
    validas = [
        "42",
        "(1+2)*3",
        "12 + (34 - 5)/6",
        "1+2*3",
        "((1+2)*3)/4",
        "007 + 1"   # ejemplo con ceros a la izquierda
    ]

    invalidas = [
        "+12",
        "1 2",
        "(1+2",
        "2*)3",
        "1++2",
        "1**2",
        "1+",
        "( )",
        ""
    ]

    print("=== PRUEBAS AUTOMÁTICAS ===\n")
    print("Expresiones válidas esperadas:")
    probar_lista_expresiones(validas)

    print("\nExpresiones inválidas esperadas:")
    probar_lista_expresiones(invalidas)

    print("\n=== INICIANDO VISTA PREVIA INTERACTIVA ===\n")
    interactive_preview()
def evaluate_expression(expr):
    """Valida y evalúa una expresión."""
    ok, msg = validate_expression(expr)
    if not ok:
        return False, msg, None

    tokens = tokenize(expr)
    parser = Parser(tokens)

    try:
        result = parser.expr()
        return True, None, result
    except ParserError as e:
        return False, e.message, None
