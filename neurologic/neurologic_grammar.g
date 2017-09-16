CONSTANT: LCASE_LETTER (LETTER | DIGIT | "_" )*
         | SIGNED_NUMBER
VARIABLE: (UCASE_LETTER | "_") (LETTER | DIGIT | "_")*
ACTIVATION_FUNCTION:  LETTER (LETTER | DIGIT)*
PREDICATE: /(?!member|_member)[a-zA-Z_][a-zA-Z0-9_]*/
INTERNAL_PREDICATE: "@" (LETTER | DIGIT)*
_IMPLIED_BY: ":-"
_LANGLE: "<"
_RANGLE: ">"
_LBRACKET: "["
_RBRACKET: "]"
_LPAREN: "("
_RPAREN: ")"
_DOT: "."
_COMMA: ","
MEMBER_PREDICATE: "member" | "_member"
_SLASH: "/"
_CARET: "^"
TRUE: "true"

?term: CONSTANT | VARIABLE
term_list: _LPAREN (term (_COMMA term)*)? _RPAREN
member_term_list: _LPAREN VARIABLE _COMMA (constant_list | VARIABLE) _RPAREN

normal_atomic_formula: PREDICATE term_list
member_formula:  MEMBER_PREDICATE member_term_list
builtin_formula: INTERNAL_PREDICATE term_list | TRUE
?special_formula: member_formula | builtin_formula
?atomic_formula:  special_formula | normal_atomic_formula

constant_list: _LBRACKET (CONSTANT (_COMMA CONSTANT)*)? _RBRACKET

fact: weight? atomic_formula _DOT

weighted_conjunction: weight atomic_formula (_COMMA atomic_formula)* _DOT

weight: _LANGLE SIGNED_NUMBER _RANGLE -> fixed_weight
     | SIGNED_NUMBER -> initial_weight

metadata_value: ACTIVATION_FUNCTION
        | _CARET VARIABLE -> specialization_variable
metadata: _LBRACKET (metadata_value (_COMMA metadata_value)*)? _RBRACKET

rule: weight? atomic_formula _IMPLIED_BY atomic_formula (_COMMA atomic_formula)* _DOT metadata?

predicate_metadata: (PREDICATE | INTERNAL_PREDICATE) _SLASH INT metadata
predicate_offset: (PREDICATE | INTERNAL_PREDICATE) _SLASH INT weight

?rule_line: rule | fact | predicate_metadata | predicate_offset
?example_line: rule
?old_example_line: weighted_conjunction
rule_file: rule_line+ | example_line+ | old_example_line+

%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.INT
%import common.LETTER
%import common.LCASE_LETTER
%import common.UCASE_LETTER
%import common.DIGIT
%import common.WS_INLINE
%import common.WS
%ignore WS


