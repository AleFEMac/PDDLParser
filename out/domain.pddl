(define (domain gripper-strips)

	(:predicates (room ?r) (ball ?b) (gripper ?g) (at-robby ?r) (at ?b ?r) (free ?g) (carry ?o ?g) (light))

	(:action move
		:parameters ( ?from ?to )
		:precondition (and (room ?from) (room ?to) (at-robby ?from))
		:effect (and (at-robby ?to) (not (at-robby ?from)) (increase (total-cost) 6)))
	
	(:action pick
		:parameters ( ?obj ?room ?gripper )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and (carry ?obj ?gripper) (not (at ?obj ?room))   (not (free ?gripper))(increase (total-cost) 2)))
	
	(:action drop
		:parameters ( ?obj ?room ?gripper )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper)    (carry ?obj ?gripper) (at-robby ?room))
		:effect (and (at ?obj ?room) (free ?gripper)   (not (carry ?obj ?gripper))(increase (total-cost) 1)))
	
	(:action move_pick
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 ?par_4 ?par_5 )
		:precondition (or (and (and (room ?par_3) (room ?par_2) (at-robby ?par_3)) (and (room ?par_3) (room ?par_2) (at-robby ?par_3))) (and (and (at-robby ?par_2) (not (at-robby ?par_3)) (increase (total-cost) 6)) (and (room ?par_3) (room ?par_2) (at-robby ?par_3))) )
		:effect (and ((and (at-robby ?par_2 ) (not (at-robby ?par_3 )) ) ) ( (and (at-robby ?par_2 ) (not (at-robby ?par_3 )) ) )(increase (total-cost) 12) ))
	
	(:action move_pick_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 ?par_4 ?par_5 )
		:precondition (or (and (and (room ?par_2) (room ?par_3) (at-robby ?par_2)) (and (room ?par_2) (room ?par_3) (at-robby ?par_2))) (and (and (at-robby ?par_3) (not (at-robby ?par_2)) (increase (total-cost) 6)) (and (room ?par_2) (room ?par_3) (at-robby ?par_2))) )
		:effect (and ((and (at-robby ?par_3 ) (not (at-robby ?par_2 )) ) ) ( (and (at-robby ?par_3 ) (not (at-robby ?par_2 )) ) )(increase (total-cost) 12) ))
	
	(:action move_drop
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 ?par_4 ?par_5 )
		:precondition (or (and (and (room ?par_3) (room ?par_2) (at-robby ?par_3)) (and (room ?par_3) (room ?par_2) (at-robby ?par_3))) (and (and (at-robby ?par_2) (not (at-robby ?par_3)) (increase (total-cost) 6)) (and (room ?par_3) (room ?par_2) (at-robby ?par_3))) )
		:effect (and ((and (at-robby ?par_2 ) (not (at-robby ?par_3 )) ) ) ( (and (at-robby ?par_2 ) (not (at-robby ?par_3 )) ) )(increase (total-cost) 12) ))
	
	(:action move_drop_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 ?par_4 ?par_5 )
		:precondition (or (and (and (room ?par_2) (room ?par_3) (at-robby ?par_2)) (and (room ?par_2) (room ?par_3) (at-robby ?par_2))) (and (and (at-robby ?par_3) (not (at-robby ?par_2)) (increase (total-cost) 6)) (and (room ?par_2) (room ?par_3) (at-robby ?par_2))) )
		:effect (and ((and (at-robby ?par_3 ) (not (at-robby ?par_2 )) ) ) ( (and (at-robby ?par_3 ) (not (at-robby ?par_2 )) ) )(increase (total-cost) 12) ))
	
	(:action pick_move
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) (and (and (carry ?par_2 ?par_0) (not (at ?par_2 ?par_1))   (not (free ?par_0))(increase (total-cost) 2)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) )
		:effect (and ((and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) ) ( (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) )(increase (total-cost) 4) ))
	
	(:action pick_move_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) (and (and (carry ?par_2 ?par_0) (not (at ?par_2 ?par_1))   (not (free ?par_0))(increase (total-cost) 2)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) )
		:effect (and ((and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) ) ( (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) )(increase (total-cost) 4) ))
	
	(:action pick_drop
		:parameters ( ?par_0 ?par_1 ?par_2 )
		:precondition (or (and (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) (and (and (carry ?par_2 ?par_0) (not (at ?par_2 ?par_1))   (not (free ?par_0))(increase (total-cost) 2)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) )
		:effect (and ((and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) ) ( (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) )(increase (total-cost) 4) ))
	
	(:action drop_move
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1))) (and (and (at ?par_2 ?par_1) (free ?par_0)   (not (carry ?par_2 ?par_0))(increase (total-cost) 1)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1))) )
		:effect (and ((and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) ) ( (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) )(increase (total-cost) 2) ))
	
	(:action drop_move_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1))) (and (and (at ?par_2 ?par_1) (free ?par_0)   (not (carry ?par_2 ?par_0))(increase (total-cost) 1)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1))) )
		:effect (and ((and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) ) ( (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) )(increase (total-cost) 2) ))
	
	(:action drop_pick
		:parameters ( ?par_0 ?par_1 ?par_2 )
		:precondition (or (and (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1))) (and (and (at ?par_2 ?par_1) (free ?par_0)   (not (carry ?par_2 ?par_0))(increase (total-cost) 1)) (and (ball ?par_2) (room ?par_1) (gripper ?par_0)    (carry ?par_2 ?par_0) (at-robby ?par_1))) )
		:effect (and ((and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) ) ( (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) )(increase (total-cost) 2) ))
)