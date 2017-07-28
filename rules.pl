0.0 cardGroupOnPlace(CardGroup,Place) :- cardOnPlace(Suit,Rank,Place),_member(Suit,[spades,diamonds,hearts,clubs]),_member(Rank,[2,3,4,5]),_member(CardGroup,[2,3,4,5]). [^Suit,^Rank,^CardGroup]
0.0 score() :- cardGroupOnPlace(CardType1,Place1),follows(CardType1,CardType2),cardGroupOnPlace(CardType2,Place2),@alldiff(Place1,Place2),_member(CardType1,[2,3,4]). [^CardType1]
<1.0> follows(2,3).    
<1.0> follows(3,4).    
<1.0> follows(4,5).    