/**
 * Created by janstudeny on 20/07/2017.
 */
define({


// prefix ID for regular expressions used in the grammar
    "RegExpID": "RE::",
    "Extra": {
        // combine multiple token matchers in order by "+",
        "match": "brackets+parens"
    },

// Style model
    "Style": {
        "comment": "comment"
        , "atom": "atom"
        , "number": "number"
        , "string": "string"
        , "error": "error"
        , "PREDICATE": "attribute"
        , "VARIABLE": "string"
        , "CONSTANT": "string-2"
        , "_IMPLIED_BY": "operator"
        , "_SLASH": "operator"
        , "SIGNED_NUMBER": "number"
        , "INT": "number"
        , "ACTIVATION_FUNCTION": "builtin"
    },

// Lexical model
    "Lex": {

        "comment:comment": {"interleave": true, "tokens": [["//", null], ["/*", "*/"]]}
        , "SIGNED_NUMBER": [
            // floats
            "RE::/\\d*\\.\\d+(e[\\+\\-]?\\d+)?/",
            "RE::/\\d+\\.\\d*/",
            "RE::/\\.\\d+/",
            // integers
            // hex
            "RE::/0x[0-9a-fA-F]+L?/",
            // binary
            "RE::/0b[01]+L?/",
            // octal
            "RE::/0o[0-7]+L?/",
            // decimal
            "RE::/[1-9]\\d*(e[\\+\\-]?\\d+)?L?/",
            // just zero
            "RE::/0(?![\\dx])/"
        ]
        , "INT": "RE::/[0-9]+/"
        , "PREDICATE": "RE::/[a-zA-Z_][a-zA-Z0-9_]*/"
        , "VARIABLE": "RE::/[A-Z_][_a-zA-Z0-9]*/"
        , "CONSTANT": ["RE::/[0-9]+/", "RE::/[a-z][a-zA-Z0-9]*/"]
        , "ACTIVATION_FUNCTION": "RE::/[a-zA-Z_][a-zA-Z0-9_]*/"
        , "INTERNAL_PREDICATE": "RE::/@[a-zA-Z0-9_]+/",
        "_IMPLIED_BY": ":-",
        "_LANGLE": "<",
        "_RANGLE": ">",
        "_LBRACKET": "[",
        "_RBRACKET": "]",
        "_LPAREN": "(",
        "_RPAREN": ")",
        "_DOT": ".",
        "_COMMA": ",",
        "MEMBER_PREDICATE": ["member", "_member"],
        "_SLASH": "/",
        "_CARET": "^",
        "TRUE": "true"
    },

// Syntax model (optional)
    "Syntax": {

        "term": "CONSTANT | VARIABLE | constant_list",
        "term_list": "_LPAREN (term (_COMMA term)*)? _RPAREN",
        "normal_atomic_formula": "PREDICATE term_list",
        "builtin_formula": "INTERNAL_PREDICATE term_list | TRUE",
        "special_formula": "builtin_formula",
        "atomic_formula": "special_formula | normal_atomic_formula",

        "constant_list": "_LBRACKET (CONSTANT (_COMMA CONSTANT)*)? _RBRACKET",


        "fact": "atomic_formula _DOT",

        "weighted_fact": "weight fact",

        "weight": "_LANGLE SIGNED_NUMBER _RANGLE | SIGNED_NUMBER",

        "metadata_value": "ACTIVATION_FUNCTION | _CARET VARIABLE",
        "metadata": "_LBRACKET (metadata_value (_COMMA metadata_value)*)? _RBRACKET",

        "weighted_rule_without_metadata": "weight rule",
        "weighted_rule_with_metadata": "weighted_rule_without_metadata metadata",
        "weighted_rule": "weighted_rule_without_metadata | weighted_rule_with_metadata",

        "rule_rest": "_IMPLIED_BY atomic_formula (_COMMA atomic_formula)* _DOT metadata?",
        "fact_rest": "_DOT metadata?",
        "offset_or_metadata": "_SLASH INT (weight | metadata)",
        "fact_or_rule" : "term_list (rule_rest | fact_rest)",
        "unweighted_line": "PREDICATE (offset_or_metadata | fact_or_rule)",
		"weighted_line": "weight PREDICATE fact_or_rule",
        "meaningful_line": "weighted_line | unweighted_line",
        "rule_file": "meaningful_line+"
    },


// what to parse and in what order
// allow comments in json ;)
    "Parser": ["rule_file"]

});