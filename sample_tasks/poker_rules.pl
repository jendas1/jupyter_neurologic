0.0 cardFromGroup(Group,Position) :- card(Position,Rank,Suit),
                                     range(GroupRange,2,5),
                                     member(Group,GroupRange),
                                     range(RankRange,2,5),
                                     member(Rank,RankRange),
                                     member(Suit,[hearts,diamonds,clubs,spades]). [^Rank,^Suit,^Group,lukasiewicz]
<1.0> straight(SucGroup) :- cardFromGroup(Group,Position1),succ(Group,SucGroup),
                        cardFromGroup(SucGroup,Position2),@alldiff(Position1,Position2),
                        range(SucGroupRange,3,5),member(SucGroup,SucGroupRange). [^SucGroup,lukasiewicz]
<3.0> score() :- straight(3). [lukasiewicz]
<4.0> score() :- straight(4). [lukasiewicz]
<5.0> score() :- straight(5). [lukasiewicz]
<1.0> succ(0,1) :- @true(a).
<1.0> succ(1,2) :- @true(a).
<1.0> succ(2,3) :- @true(a).
<1.0> succ(3,4) :- @true(a).
<1.0> succ(4,5) :- @true(a).
score/0 [identity]