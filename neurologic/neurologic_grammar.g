CONSTANT: LCASE_LETTER (LETTER | DIGIT)*
         | SIGNED_NUMBER
VARIABLE: (UCASE_LETTER | "_") (LETTER | DIGIT | "_")*
ACTIVATION_FUNCTION:  LETTER (LETTER | DIGIT)*
PREDICATE: (LETTER | "_") (LETTER | DIGIT | "_")*
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

term: CONSTANT | VARIABLE
term_list: _LPAREN (term (_COMMA term)*)? _RPAREN
member_term_list: _LPAREN VARIABLE _COMMA constant_list _RPAREN

normal_atomic_formula: PREDICATE term_list
member_formula:  MEMBER_PREDICATE member_term_list
builtin_formula: INTERNAL_PREDICATE term_list | TRUE
special_formula: member_formula | builtin_formula
atomic_formula:  special_formula | normal_atomic_formula

constant_list: _LBRACKET (CONSTANT (_COMMA CONSTANT)*)? _RBRACKET
rule: atomic_formula _IMPLIED_BY atomic_formula (_COMMA atomic_formula)* _DOT

fact: atomic_formula _DOT

weighted_fact: weight fact

weighted_conjunction: weight atomic_formula (_COMMA atomic_formula)* _DOT

weight: _LANGLE SIGNED_NUMBER _RANGLE -> fixed_weight
     | SIGNED_NUMBER -> initial_weight

metadata_value: ACTIVATION_FUNCTION
        | _CARET VARIABLE -> specialization_variable
metadata: _LBRACKET (metadata_value (_COMMA metadata_value)*)? _RBRACKET

weighted_rule_without_metadata: weight rule
weighted_rule_with_metadata: weighted_rule_without_metadata metadata
weighted_rule: weighted_rule_without_metadata
        | weighted_rule_with_metadata

predicate_metadata: PREDICATE _SLASH INT metadata
predicate_offset: PREDICATE _SLASH INT weight

meaningful_line: weighted_rule | rule | weighted_fact | fact | predicate_metadata | predicate_offset
rule_file: meaningful_line+
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


