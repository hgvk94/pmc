(set-option :fixedpoint.engine spacer)
(declare-rel h1 (Int Int) )
(declare-rel h2 (Int Int Int) )
(declare-rel h3 (Int Int Int Int) )
(declare-rel Error ( ))
(declare-var sent_bit Int)
(declare-var n Int)
(declare-var received_sig Int)
(declare-var received_bit Int)

( rule (=> ( and (< n -0.253347103136) (>= n -0.841621233573)  )( and (< n -0.253347103136) (>= n -0.841621233573)  )( h1 sent_bit n )))
( rule (=> ( and ( h1 sent_bit n ) ( = received_sig ( + sent_bit n ) )) ( h2 sent_bit n received_sig )))
( rule (=> ( and ( h2 sent_bit n received_sig ) ( or ( and ( > received_sig 0.5 ) ( = received_bit 1.0 ) )( and  ( not( > received_sig 0.5 ) ) ( = received_bit 0.0 )) )) ( h3 sent_bit n received_sig received_bit )))
( rule (=> ( and ( h3 sent_bit n received_sig received_bit ) ( or ( not( or ( = sent_bit 1.0 ) ( = sent_bit 0.0 ) ) ) ( = sent_bit received_bit ) )) Error))
(query Error)
