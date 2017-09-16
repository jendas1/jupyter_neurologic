0.0 cardFromGroup(Group,Position) :- card(Position,Rank,Suit),
                                     range(GroupRange,2,3),
                                     member(Group,RankRange),
                                     range(RankRange,2,3),
                                     member(Rank,RankRange),
                                     member(Suit,[hearts]). [^Rank,^Suit,^Group,lukasiewicz]
0.0 straight(SucGroup) :- cardFromGroup(Group,Position1),succ(2,3),
                        cardFromGroup(SucGroup,Position2),@alldiff(Position1,Position2),
                        range(SucGroupRange,3,3),member(SucGroup,SucGroupRange). [^SucGroup,lukasiewicz]
0.0 score() :- straight(Group),range(GroupRange,3,3),member(Group,GroupRange). [^Group]
<1.0> succ(2,3) :- @true(a).
score/0 [identity]