from neurologic.template_transformer import transform


def test_special_predicate():
    assert transform(range_input_text) == range_result


def test_advanced_template_transform():
    assert transform(advanced_input_text) == advanced_result


advanced_input_text = r"""
0.0 cardFromGroup(Group,Position) :- card(Position,Rank,Suit),
                                     range(GroupRange,2,2),
                                     member(Group,RankRange),
                                     range(RankRange,2,2),
                                     member(Rank,RankRange),
                                     member(Suit,[hearts,diamonds,clubs,spades]). [^Rank,^Suit,^Group,lukasiewicz]
0.0 straight(SucGroup) :- cardFromGroup(Group,Position1),succ(Group,SucGroup),
                        cardFromGroup(SucGroup,Position2),@alldiff(Position1,Position2),
                        range(SucGroupRange,3,3),member(SucGroup,SucGroupRange). [^SucGroup,lukasiewicz]
0.0 score() :- straight(Group),range(GroupRange,3,3),member(Group,GroupRange). [^Group]
<1.0> succ(0,1).
<1.0> succ(1,2).
<1.0> succ(2,3).
<1.0> succ(3,4).
<1.0> succ(4,5).
score/0 [identity]
"""

advanced_result = """\
__Var0_cardFromGroup(2,Position) :- card(Position,2,hearts).
0.0 cardFromGroup(2,Position) :- __Var0_cardFromGroup(2,Position).
__Var0_cardFromGroup/2 [lukasiewicz]
__Var1_cardFromGroup(2,Position) :- card(Position,2,diamonds).
0.0 cardFromGroup(2,Position) :- __Var1_cardFromGroup(2,Position).
__Var1_cardFromGroup/2 [lukasiewicz]
__Var2_cardFromGroup(2,Position) :- card(Position,2,clubs).
0.0 cardFromGroup(2,Position) :- __Var2_cardFromGroup(2,Position).
__Var2_cardFromGroup/2 [lukasiewicz]
__Var3_cardFromGroup(2,Position) :- card(Position,2,spades).
0.0 cardFromGroup(2,Position) :- __Var3_cardFromGroup(2,Position).
__Var3_cardFromGroup/2 [lukasiewicz]
__Var0_straight(3) :- cardFromGroup(Group,Position1),succ(Group,3),cardFromGroup(3,Position2),@alldiff(Position1,Position2).
0.0 straight(3) :- __Var0_straight(3).
__Var0_straight/1 [lukasiewicz]
__Var0_score(a) :- straight(3).
0.0 score(a) :- __Var0_score(a).
<1.0> succ(0,1).
<1.0> succ(1,2).
<1.0> succ(2,3).
<1.0> succ(3,4).
<1.0> succ(4,5).
score/1 [identity]
__Var0_finalKappa(a) :- cardFromGroup(__X0,__X1),__finalcardFromGroup(__X0,__X1).
<1.0> finalKappa(a) :- __Var0_finalKappa(a).
__Var0_finalKappa/1 [identity]
__Var1_finalKappa(a) :- card(__X0,__X1,__X2),__finalcard(__X0,__X1,__X2).
<1.0> finalKappa(a) :- __Var1_finalKappa(a).
__Var1_finalKappa/1 [identity]
__Var2_finalKappa(a) :- straight(__X0),__finalstraight(__X0).
<1.0> finalKappa(a) :- __Var2_finalKappa(a).
__Var2_finalKappa/1 [identity]
__Var3_finalKappa(a) :- succ(__X0,__X1),__finalsucc(__X0,__X1).
<1.0> finalKappa(a) :- __Var3_finalKappa(a).
__Var3_finalKappa/1 [identity]
__Var4_finalKappa(a) :- score(__X0),__finalscore(__X0).
<1.0> finalKappa(a) :- __Var4_finalKappa(a).
__Var4_finalKappa/1 [identity]
finalKappa/1 [identity]
cardFromGroup/2 <0.0>
card/3 <0.0>
straight/1 <0.0>
succ/2 <0.0>
score/1 <0.0>
finalKappa/1 <0.0>
__finalcardFromGroup/2 <0.0>
__finalcard/3 <0.0>
__finalstraight/1 <0.0>
__finalsucc/2 <0.0>
__finalscore/1 <0.0>\
"""

range_input_text = r"""
0.0 winner(Group1,Group2) :- nice(jenda),range(Group1Range,1,3),_member(Group1,Group1Range)
                                        ,range(Group2Range,a,c),_member(Group2,Group2Range). [lukasiewicz,^Group1,^Group2]
0.0 winner(xyz,abc) :- nice(jenda). [lukasiewicz]
"""

range_result = """\
__Var0_winner(1,a) :- nice(jenda).
0.0 winner(1,a) :- __Var0_winner(1,a).
__Var0_winner/2 [lukasiewicz]
__Var1_winner(1,b) :- nice(jenda).
0.0 winner(1,b) :- __Var1_winner(1,b).
__Var1_winner/2 [lukasiewicz]
__Var2_winner(1,c) :- nice(jenda).
0.0 winner(1,c) :- __Var2_winner(1,c).
__Var2_winner/2 [lukasiewicz]
__Var3_winner(2,a) :- nice(jenda).
0.0 winner(2,a) :- __Var3_winner(2,a).
__Var3_winner/2 [lukasiewicz]
__Var4_winner(2,b) :- nice(jenda).
0.0 winner(2,b) :- __Var4_winner(2,b).
__Var4_winner/2 [lukasiewicz]
__Var5_winner(2,c) :- nice(jenda).
0.0 winner(2,c) :- __Var5_winner(2,c).
__Var5_winner/2 [lukasiewicz]
__Var6_winner(3,a) :- nice(jenda).
0.0 winner(3,a) :- __Var6_winner(3,a).
__Var6_winner/2 [lukasiewicz]
__Var7_winner(3,b) :- nice(jenda).
0.0 winner(3,b) :- __Var7_winner(3,b).
__Var7_winner/2 [lukasiewicz]
__Var8_winner(3,c) :- nice(jenda).
0.0 winner(3,c) :- __Var8_winner(3,c).
__Var8_winner/2 [lukasiewicz]
__Var9_winner(xyz,abc) :- nice(jenda).
0.0 winner(xyz,abc) :- __Var9_winner(xyz,abc).
__Var9_winner/2 [lukasiewicz]
__Var0_finalKappa(a) :- winner(__X0,__X1),__finalwinner(__X0,__X1).
<1.0> finalKappa(a) :- __Var0_finalKappa(a).
__Var0_finalKappa/1 [identity]
__Var1_finalKappa(a) :- nice(__X0),__finalnice(__X0).
<1.0> finalKappa(a) :- __Var1_finalKappa(a).
__Var1_finalKappa/1 [identity]
finalKappa/1 [identity]
winner/2 <0.0>
nice/1 <0.0>
finalKappa/1 <0.0>
__finalwinner/2 <0.0>
__finalnice/1 <0.0>\
"""
