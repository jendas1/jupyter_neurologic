from neurologic.template_transformer import RangePredicateTransformer, neurologic_parser, ToCodeTransformer, \
    RuleSpecializationTransformer


def apply_transformer_to_text(text, transformer):
    tree = neurologic_parser.parse(text)
    transformed_tree = transformer.transform(tree)
    return ToCodeTransformer().transform(transformed_tree)


def test_range_transformer():
    input = "0.0 score() :- letter(List),range(ListRange,a,z),member(List,ListRange). [^List]"
    output = "0.0 score() :- letter(List),member(List,[a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z]). [^List]"
    assert apply_transformer_to_text(input, RangePredicateTransformer()) == output


def test_specialization_transformer():
    assert apply_transformer_to_text(specialization_input, RuleSpecializationTransformer()) == specialization_output


specialization_input = "0.0 score() :- letter(List),member(List,[a,b,c,d,e,f]). [^List]"

specialization_output = """\
0.0 score() :- letter(a).
0.0 score() :- letter(b).
0.0 score() :- letter(c).
0.0 score() :- letter(d).
0.0 score() :- letter(e).
0.0 score() :- letter(f)."""
