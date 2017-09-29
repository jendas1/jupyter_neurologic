from neurologic import template_transformer


def test_transform_result():
    assert template_transformer.transform_result(input) == output


input = """\
__Var2_score(a__) :- straight(5).
__Var1_score(a__) :- straight(4).
__Var0_score(a__) :- straight(3).
__Var63_cardFromGroup(5,Position) :- card(Position,5,spades).
__Var62_cardFromGroup(4,Position) :- card(Position,5,spades).
__Var61_cardFromGroup(3,Position) :- card(Position,5,spades).
__Var60_cardFromGroup(2,Position) :- card(Position,5,spades).
__Var59_cardFromGroup(5,Position) :- card(Position,5,clubs).
__Var58_cardFromGroup(4,Position) :- card(Position,5,clubs).
__Var57_cardFromGroup(3,Position) :- card(Position,5,clubs).
__Var56_cardFromGroup(2,Position) :- card(Position,5,clubs).
__Var55_cardFromGroup(5,Position) :- card(Position,5,diamonds).
__Var54_cardFromGroup(4,Position) :- card(Position,5,diamonds).
__Var53_cardFromGroup(3,Position) :- card(Position,5,diamonds).
__Var52_cardFromGroup(2,Position) :- card(Position,5,diamonds).
__Var51_cardFromGroup(5,Position) :- card(Position,5,hearts).
__Var50_cardFromGroup(4,Position) :- card(Position,5,hearts).
__Var49_cardFromGroup(3,Position) :- card(Position,5,hearts).
__Var48_cardFromGroup(2,Position) :- card(Position,5,hearts).
__Var47_cardFromGroup(5,Position) :- card(Position,4,spades).
__Var46_cardFromGroup(4,Position) :- card(Position,4,spades).
__Var45_cardFromGroup(3,Position) :- card(Position,4,spades).
__Var44_cardFromGroup(2,Position) :- card(Position,4,spades).
__Var43_cardFromGroup(5,Position) :- card(Position,4,clubs).
__Var42_cardFromGroup(4,Position) :- card(Position,4,clubs).
__Var41_cardFromGroup(3,Position) :- card(Position,4,clubs).
__Var40_cardFromGroup(2,Position) :- card(Position,4,clubs).
__Var39_cardFromGroup(5,Position) :- card(Position,4,diamonds).
__Var38_cardFromGroup(4,Position) :- card(Position,4,diamonds).
__Var37_cardFromGroup(3,Position) :- card(Position,4,diamonds).
__Var36_cardFromGroup(2,Position) :- card(Position,4,diamonds).
__Var35_cardFromGroup(5,Position) :- card(Position,4,hearts).
__Var34_cardFromGroup(4,Position) :- card(Position,4,hearts).
__Var33_cardFromGroup(3,Position) :- card(Position,4,hearts).
__Var32_cardFromGroup(2,Position) :- card(Position,4,hearts).
__Var31_cardFromGroup(5,Position) :- card(Position,3,spades).
__Var30_cardFromGroup(4,Position) :- card(Position,3,spades).
__Var29_cardFromGroup(3,Position) :- card(Position,3,spades).
__Var28_cardFromGroup(2,Position) :- card(Position,3,spades).
__Var27_cardFromGroup(5,Position) :- card(Position,3,clubs).
__Var26_cardFromGroup(4,Position) :- card(Position,3,clubs).
__Var25_cardFromGroup(3,Position) :- card(Position,3,clubs).
__Var24_cardFromGroup(2,Position) :- card(Position,3,clubs).
__Var23_cardFromGroup(5,Position) :- card(Position,3,diamonds).
__Var22_cardFromGroup(4,Position) :- card(Position,3,diamonds).
__Var21_cardFromGroup(3,Position) :- card(Position,3,diamonds).
__Var20_cardFromGroup(2,Position) :- card(Position,3,diamonds).
__Var19_cardFromGroup(5,Position) :- card(Position,3,hearts).
__Var18_cardFromGroup(4,Position) :- card(Position,3,hearts).
__Var17_cardFromGroup(3,Position) :- card(Position,3,hearts).
__Var16_cardFromGroup(2,Position) :- card(Position,3,hearts).
__Var15_cardFromGroup(5,Position) :- card(Position,2,spades).
__Var14_cardFromGroup(4,Position) :- card(Position,2,spades).
__Var13_cardFromGroup(3,Position) :- card(Position,2,spades).
__Var12_cardFromGroup(2,Position) :- card(Position,2,spades).
__Var11_cardFromGroup(5,Position) :- card(Position,2,clubs).
__Var10_cardFromGroup(4,Position) :- card(Position,2,clubs).
__Var9_cardFromGroup(3,Position) :- card(Position,2,clubs).
__Var8_cardFromGroup(2,Position) :- card(Position,2,clubs).
__Var7_cardFromGroup(5,Position) :- card(Position,2,diamonds).
__Var6_cardFromGroup(4,Position) :- card(Position,2,diamonds).
__Var5_cardFromGroup(3,Position) :- card(Position,2,diamonds).
__Var4_cardFromGroup(2,Position) :- card(Position,2,diamonds).
__Var3_cardFromGroup(5,Position) :- card(Position,2,hearts).
__Var2_cardFromGroup(4,Position) :- card(Position,2,hearts).
__Var1_cardFromGroup(3,Position) :- card(Position,2,hearts).
__Var0_cardFromGroup(2,Position) :- card(Position,2,hearts).
__Var4_succ(4,5) :- @true(a).
__Var3_succ(3,4) :- @true(a).
__Var2_succ(2,3) :- @true(a).
__Var1_succ(1,2) :- @true(a).
__Var0_succ(0,1) :- @true(a).
__Var2_straight(5) :- cardFromGroup(Group,Position1),succ(Group,5),cardFromGroup(5,Position2),@alldiff(Position1,Position2).
__Var1_straight(4) :- cardFromGroup(Group,Position1),succ(Group,4),cardFromGroup(4,Position2),@alldiff(Position1,Position2).
__Var0_straight(3) :- cardFromGroup(Group,Position1),succ(Group,3),cardFromGroup(3,Position2),@alldiff(Position1,Position2).
5.000000000000000 score(a__) :- __Var2_score(a__).
4.000000000000000 score(a__) :- __Var1_score(a__).
3.000000000000000 score(a__) :- __Var0_score(a__).
0.028214306559451 cardFromGroup(5,Position) :- __Var63_cardFromGroup(5,Position).
-0.077682533337182 cardFromGroup(4,Position) :- __Var62_cardFromGroup(4,Position).
-0.107587110777089 cardFromGroup(3,Position) :- __Var61_cardFromGroup(3,Position).
0.007255280245345 cardFromGroup(2,Position) :- __Var60_cardFromGroup(2,Position).
-0.044209382485792 cardFromGroup(5,Position) :- __Var59_cardFromGroup(5,Position).
-0.189016488152916 cardFromGroup(4,Position) :- __Var58_cardFromGroup(4,Position).
0.124997048186925 cardFromGroup(3,Position) :- __Var57_cardFromGroup(3,Position).
-0.041585402893142 cardFromGroup(2,Position) :- __Var56_cardFromGroup(2,Position).
-0.097570742848824 cardFromGroup(5,Position) :- __Var55_cardFromGroup(5,Position).
-0.157260703454614 cardFromGroup(4,Position) :- __Var54_cardFromGroup(4,Position).
-0.116841625838388 cardFromGroup(3,Position) :- __Var53_cardFromGroup(3,Position).
0.101624073117556 cardFromGroup(2,Position) :- __Var52_cardFromGroup(2,Position).
0.555242660365573 cardFromGroup(5,Position) :- __Var51_cardFromGroup(5,Position).
-0.193419394933759 cardFromGroup(4,Position) :- __Var50_cardFromGroup(4,Position).
-0.103966257445005 cardFromGroup(3,Position) :- __Var49_cardFromGroup(3,Position).
0.207828207015615 cardFromGroup(2,Position) :- __Var48_cardFromGroup(2,Position).
-0.028636459312018 cardFromGroup(5,Position) :- __Var47_cardFromGroup(5,Position).
-0.122412074673275 cardFromGroup(4,Position) :- __Var46_cardFromGroup(4,Position).
-0.075756946760247 cardFromGroup(3,Position) :- __Var45_cardFromGroup(3,Position).
0.713417709838410 cardFromGroup(2,Position) :- __Var44_cardFromGroup(2,Position).
-0.061865168500123 cardFromGroup(5,Position) :- __Var43_cardFromGroup(5,Position).
0.058286556553856 cardFromGroup(4,Position) :- __Var42_cardFromGroup(4,Position).
0.135719793007952 cardFromGroup(3,Position) :- __Var41_cardFromGroup(3,Position).
0.026429555155515 cardFromGroup(2,Position) :- __Var40_cardFromGroup(2,Position).
-0.061335355912881 cardFromGroup(5,Position) :- __Var39_cardFromGroup(5,Position).
-0.156744687564974 cardFromGroup(4,Position) :- __Var38_cardFromGroup(4,Position).
-0.102929600520500 cardFromGroup(3,Position) :- __Var37_cardFromGroup(3,Position).
0.132006578170979 cardFromGroup(2,Position) :- __Var36_cardFromGroup(2,Position).
0.084661845236943 cardFromGroup(5,Position) :- __Var35_cardFromGroup(5,Position).
0.191128001307874 cardFromGroup(4,Position) :- __Var34_cardFromGroup(4,Position).
0.632825623168856 cardFromGroup(3,Position) :- __Var33_cardFromGroup(3,Position).
0.067072397575594 cardFromGroup(2,Position) :- __Var32_cardFromGroup(2,Position).
0.229444244023400 cardFromGroup(5,Position) :- __Var31_cardFromGroup(5,Position).
-0.130177778463119 cardFromGroup(4,Position) :- __Var30_cardFromGroup(4,Position).
-0.076884884930447 cardFromGroup(3,Position) :- __Var29_cardFromGroup(3,Position).
-0.053768039162250 cardFromGroup(2,Position) :- __Var28_cardFromGroup(2,Position).
0.308675981120340 cardFromGroup(5,Position) :- __Var27_cardFromGroup(5,Position).
0.097988983308011 cardFromGroup(4,Position) :- __Var26_cardFromGroup(4,Position).
-0.114847924391183 cardFromGroup(3,Position) :- __Var25_cardFromGroup(3,Position).
0.056575463291055 cardFromGroup(2,Position) :- __Var24_cardFromGroup(2,Position).
-0.058887310828210 cardFromGroup(5,Position) :- __Var23_cardFromGroup(5,Position).
-0.146273343309422 cardFromGroup(4,Position) :- __Var22_cardFromGroup(4,Position).
-0.079362839981708 cardFromGroup(3,Position) :- __Var21_cardFromGroup(3,Position).
-0.005266301345607 cardFromGroup(2,Position) :- __Var20_cardFromGroup(2,Position).
0.032707543297245 cardFromGroup(5,Position) :- __Var19_cardFromGroup(5,Position).
-0.175753623892319 cardFromGroup(4,Position) :- __Var18_cardFromGroup(4,Position).
-0.088939101984608 cardFromGroup(3,Position) :- __Var17_cardFromGroup(3,Position).
0.099847405261464 cardFromGroup(2,Position) :- __Var16_cardFromGroup(2,Position).
-0.037508708400828 cardFromGroup(5,Position) :- __Var15_cardFromGroup(5,Position).
0.080593401761700 cardFromGroup(4,Position) :- __Var14_cardFromGroup(4,Position).
-0.158980258269128 cardFromGroup(3,Position) :- __Var13_cardFromGroup(3,Position).
0.028936586524051 cardFromGroup(2,Position) :- __Var12_cardFromGroup(2,Position).
0.452649398621918 cardFromGroup(5,Position) :- __Var11_cardFromGroup(5,Position).
0.026738762302627 cardFromGroup(4,Position) :- __Var10_cardFromGroup(4,Position).
0.127030404981471 cardFromGroup(3,Position) :- __Var9_cardFromGroup(3,Position).
0.141481425153147 cardFromGroup(2,Position) :- __Var8_cardFromGroup(2,Position).
-0.100546340367991 cardFromGroup(5,Position) :- __Var7_cardFromGroup(5,Position).
-0.193341566333894 cardFromGroup(4,Position) :- __Var6_cardFromGroup(4,Position).
-0.159961279870655 cardFromGroup(3,Position) :- __Var5_cardFromGroup(3,Position).
0.088253153612384 cardFromGroup(2,Position) :- __Var4_cardFromGroup(2,Position).
0.065842676096937 cardFromGroup(5,Position) :- __Var3_cardFromGroup(5,Position).
-0.142335278390447 cardFromGroup(4,Position) :- __Var2_cardFromGroup(4,Position).
-0.072453657356146 cardFromGroup(3,Position) :- __Var1_cardFromGroup(3,Position).
0.002009995494660 cardFromGroup(2,Position) :- __Var0_cardFromGroup(2,Position).
1.000000000000000 succ(4,5) :- __Var4_succ(4,5).
1.000000000000000 succ(3,4) :- __Var3_succ(3,4).
1.000000000000000 succ(2,3) :- __Var2_succ(2,3).
0.000000000000000 succ(1,2) :- __Var1_succ(1,2).
0.000000000000000 succ(0,1) :- __Var0_succ(0,1).
1.000000000000000 straight(5) :- __Var2_straight(5).
1.000000000000000 straight(4) :- __Var1_straight(4).
1.000000000000000 straight(3) :- __Var0_straight(3).
__Var4_finalKappa(a) :- score(__X0),__finalscore(__X0).
__Var3_finalKappa(a) :- card(__X0,__X1,__X2),__finalcard(__X0,__X1,__X2).
__Var2_finalKappa(a) :- cardFromGroup(__X0,__X1),__finalcardFromGroup(__X0,__X1).
__Var1_finalKappa(a) :- succ(__X0,__X1),__finalsucc(__X0,__X1).
__Var0_finalKappa(a) :- straight(__X0),__finalstraight(__X0).
1.000000000000000 finalKappa(a) :- __Var4_finalKappa(a).
0.000000000000000 finalKappa(a) :- __Var3_finalKappa(a).
0.000000000000000 finalKappa(a) :- __Var2_finalKappa(a).
0.000000000000000 finalKappa(a) :- __Var1_finalKappa(a).
0.000000000000000 finalKappa(a) :- __Var0_finalKappa(a).
@alldiff/2 0.13428322708237594
@true/1 0.2020460083732427
__finalcard/3 0.0
__finalcardFromGroup/2 0.0
__finalscore/1 0.0
__finalstraight/1 0.0
__finalsucc/2 0.0
card/3 0.0
cardFromGroup/2 0.0
finalKappa/1 0.0
score/1 0.0
straight/1 0.0
succ/2 0.0\
"""

output = """\
5.000000000000000 score() :- straight(5).
4.000000000000000 score() :- straight(4).
3.000000000000000 score() :- straight(3).
0.028214306559451 cardFromGroup(5,Position) :- card(Position,5,spades).
-0.077682533337182 cardFromGroup(4,Position) :- card(Position,5,spades).
-0.107587110777089 cardFromGroup(3,Position) :- card(Position,5,spades).
0.007255280245345 cardFromGroup(2,Position) :- card(Position,5,spades).
-0.044209382485792 cardFromGroup(5,Position) :- card(Position,5,clubs).
-0.189016488152916 cardFromGroup(4,Position) :- card(Position,5,clubs).
0.124997048186925 cardFromGroup(3,Position) :- card(Position,5,clubs).
-0.041585402893142 cardFromGroup(2,Position) :- card(Position,5,clubs).
-0.097570742848824 cardFromGroup(5,Position) :- card(Position,5,diamonds).
-0.157260703454614 cardFromGroup(4,Position) :- card(Position,5,diamonds).
-0.116841625838388 cardFromGroup(3,Position) :- card(Position,5,diamonds).
0.101624073117556 cardFromGroup(2,Position) :- card(Position,5,diamonds).
0.555242660365573 cardFromGroup(5,Position) :- card(Position,5,hearts).
-0.193419394933759 cardFromGroup(4,Position) :- card(Position,5,hearts).
-0.103966257445005 cardFromGroup(3,Position) :- card(Position,5,hearts).
0.207828207015615 cardFromGroup(2,Position) :- card(Position,5,hearts).
-0.028636459312018 cardFromGroup(5,Position) :- card(Position,4,spades).
-0.122412074673275 cardFromGroup(4,Position) :- card(Position,4,spades).
-0.075756946760247 cardFromGroup(3,Position) :- card(Position,4,spades).
0.713417709838410 cardFromGroup(2,Position) :- card(Position,4,spades).
-0.061865168500123 cardFromGroup(5,Position) :- card(Position,4,clubs).
0.058286556553856 cardFromGroup(4,Position) :- card(Position,4,clubs).
0.135719793007952 cardFromGroup(3,Position) :- card(Position,4,clubs).
0.026429555155515 cardFromGroup(2,Position) :- card(Position,4,clubs).
-0.061335355912881 cardFromGroup(5,Position) :- card(Position,4,diamonds).
-0.156744687564974 cardFromGroup(4,Position) :- card(Position,4,diamonds).
-0.102929600520500 cardFromGroup(3,Position) :- card(Position,4,diamonds).
0.132006578170979 cardFromGroup(2,Position) :- card(Position,4,diamonds).
0.084661845236943 cardFromGroup(5,Position) :- card(Position,4,hearts).
0.191128001307874 cardFromGroup(4,Position) :- card(Position,4,hearts).
0.632825623168856 cardFromGroup(3,Position) :- card(Position,4,hearts).
0.067072397575594 cardFromGroup(2,Position) :- card(Position,4,hearts).
0.229444244023400 cardFromGroup(5,Position) :- card(Position,3,spades).
-0.130177778463119 cardFromGroup(4,Position) :- card(Position,3,spades).
-0.076884884930447 cardFromGroup(3,Position) :- card(Position,3,spades).
-0.053768039162250 cardFromGroup(2,Position) :- card(Position,3,spades).
0.308675981120340 cardFromGroup(5,Position) :- card(Position,3,clubs).
0.097988983308011 cardFromGroup(4,Position) :- card(Position,3,clubs).
-0.114847924391183 cardFromGroup(3,Position) :- card(Position,3,clubs).
0.056575463291055 cardFromGroup(2,Position) :- card(Position,3,clubs).
-0.058887310828210 cardFromGroup(5,Position) :- card(Position,3,diamonds).
-0.146273343309422 cardFromGroup(4,Position) :- card(Position,3,diamonds).
-0.079362839981708 cardFromGroup(3,Position) :- card(Position,3,diamonds).
-0.005266301345607 cardFromGroup(2,Position) :- card(Position,3,diamonds).
0.032707543297245 cardFromGroup(5,Position) :- card(Position,3,hearts).
-0.175753623892319 cardFromGroup(4,Position) :- card(Position,3,hearts).
-0.088939101984608 cardFromGroup(3,Position) :- card(Position,3,hearts).
0.099847405261464 cardFromGroup(2,Position) :- card(Position,3,hearts).
-0.037508708400828 cardFromGroup(5,Position) :- card(Position,2,spades).
0.080593401761700 cardFromGroup(4,Position) :- card(Position,2,spades).
-0.158980258269128 cardFromGroup(3,Position) :- card(Position,2,spades).
0.028936586524051 cardFromGroup(2,Position) :- card(Position,2,spades).
0.452649398621918 cardFromGroup(5,Position) :- card(Position,2,clubs).
0.026738762302627 cardFromGroup(4,Position) :- card(Position,2,clubs).
0.127030404981471 cardFromGroup(3,Position) :- card(Position,2,clubs).
0.141481425153147 cardFromGroup(2,Position) :- card(Position,2,clubs).
-0.100546340367991 cardFromGroup(5,Position) :- card(Position,2,diamonds).
-0.193341566333894 cardFromGroup(4,Position) :- card(Position,2,diamonds).
-0.159961279870655 cardFromGroup(3,Position) :- card(Position,2,diamonds).
0.088253153612384 cardFromGroup(2,Position) :- card(Position,2,diamonds).
0.065842676096937 cardFromGroup(5,Position) :- card(Position,2,hearts).
-0.142335278390447 cardFromGroup(4,Position) :- card(Position,2,hearts).
-0.072453657356146 cardFromGroup(3,Position) :- card(Position,2,hearts).
0.002009995494660 cardFromGroup(2,Position) :- card(Position,2,hearts).
1.000000000000000 succ(4,5) :- @true(a).
1.000000000000000 succ(3,4) :- @true(a).
1.000000000000000 succ(2,3) :- @true(a).
0.000000000000000 succ(1,2) :- @true(a).
0.000000000000000 succ(0,1) :- @true(a).
1.000000000000000 straight(5) :- cardFromGroup(Group,Position1),succ(Group,5),cardFromGroup(5,Position2),@alldiff(Position1,Position2).
1.000000000000000 straight(4) :- cardFromGroup(Group,Position1),succ(Group,4),cardFromGroup(4,Position2),@alldiff(Position1,Position2).
1.000000000000000 straight(3) :- cardFromGroup(Group,Position1),succ(Group,3),cardFromGroup(3,Position2),@alldiff(Position1,Position2).\
"""
