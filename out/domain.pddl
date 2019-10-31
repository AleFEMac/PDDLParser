(define (domain gripper-strips)

	(:predicates (room ?r) (ball ?b) (gripper ?g) (at-robby ?r) (at ?b ?r) (free ?g) (carry ?o ?g))

	(:action move
		:parameters ( ?from ?to )
		:precondition (and (room ?from) (room ?to) (at-robby ?from))
		:effect (and (at-robby ?to) (not (at-robby ?from)))
	)
	
	(:action pick
		:parameters ( ?obj ?room ?gripper )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper) (at ?obj ?room) (at-robby ?room) (free ?gripper))
		:effect (and (carry ?obj ?gripper) (not (at ?obj ?room)) (not (free ?gripper)))
	)
	
	(:action drop
		:parameters ( ?obj ?room ?gripper )
		:precondition (and (ball ?obj) (room ?room) (gripper ?gripper) (carry ?obj ?gripper) (at-robby ?room))
		:effect (and (at ?obj ?room) (free ?gripper) (not (carry ?obj ?gripper)))
	)
	
	(:action move_pick
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (room ?par_1) (room ?par_0) (at-robby ?par_1)) (and (and (at-robby ?par_0) (not (at-robby ?par_1))) (and (room ?par_1) (room ?par_0) (at-robby ?par_1))) )
		:effect (and (and (at-robby ?par_0 ) (not (at-robby ?par_1 )) )   (and (at-robby ?par_0 ) (not (at-robby ?par_1 )) ) )
	)
	
	(:action move_pick_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (room ?par_0) (room ?par_1) (at-robby ?par_0)) (and (and (at-robby ?par_1) (not (at-robby ?par_0))) (and (room ?par_0) (room ?par_1) (at-robby ?par_0))) )
		:effect (and (and (at-robby ?par_1 ) (not (at-robby ?par_0 )) )   (and (at-robby ?par_1 ) (not (at-robby ?par_0 )) ) )
	)
	
	(:action move_drop
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (room ?par_1) (room ?par_0) (at-robby ?par_1)) (and (and (at-robby ?par_0) (not (at-robby ?par_1))) (and (room ?par_1) (room ?par_0) (at-robby ?par_1))) )
		:effect (and (and (at-robby ?par_0 ) (not (at-robby ?par_1 )) )   (and (at-robby ?par_0 ) (not (at-robby ?par_1 )) ) )
	)
	
	(:action move_drop_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (room ?par_0) (room ?par_1) (at-robby ?par_0)) (and (and (at-robby ?par_1) (not (at-robby ?par_0))) (and (room ?par_0) (room ?par_1) (at-robby ?par_0))) )
		:effect (and (and (at-robby ?par_1 ) (not (at-robby ?par_0 )) )   (and (at-robby ?par_1 ) (not (at-robby ?par_0 )) ) )
	)
	
	(:action pick_move
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0)) (and (and (carry ?par_2 ?par_0) (not (at ?par_2 ?par_1)) (not (free ?par_0))) (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) )
		:effect (and (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) )   (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) )
	)
	
	(:action pick_move_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0)) (and (and (carry ?par_2 ?par_0) (not (at ?par_2 ?par_1)) (not (free ?par_0))) (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) )
		:effect (and (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) )   (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) )
	)
	
	(:action pick_drop
		:parameters ( ?par_0 ?par_1 ?par_2 )
		:precondition (or (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0)) (and (and (carry ?par_2 ?par_0) (not (at ?par_2 ?par_1)) (not (free ?par_0))) (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (at ?par_2 ?par_1) (at-robby ?par_1) (free ?par_0))) )
		:effect (and (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) )   (and (carry ?par_2 ?par_0 ) (not (at ?par_2 ?par_1 )) (not (free ?par_0 )) ) )
	)
	
	(:action drop_move
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (carry ?par_2 ?par_0) (at-robby ?par_1)) (and (and (at ?par_2 ?par_1) (free ?par_0) (not (carry ?par_2 ?par_0))) (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (carry ?par_2 ?par_0) (at-robby ?par_1))) )
		:effect (and (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) )   (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) )
	)
	
	(:action drop_move_1
		:parameters ( ?par_0 ?par_1 ?par_2 ?par_3 )
		:precondition (or (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (carry ?par_2 ?par_0) (at-robby ?par_1)) (and (and (at ?par_2 ?par_1) (free ?par_0) (not (carry ?par_2 ?par_0))) (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (carry ?par_2 ?par_0) (at-robby ?par_1))) )
		:effect (and (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) )   (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) )
	)
	
	(:action drop_pick
		:parameters ( ?par_0 ?par_1 ?par_2 )
		:precondition (or (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (carry ?par_2 ?par_0) (at-robby ?par_1)) (and (and (at ?par_2 ?par_1) (free ?par_0) (not (carry ?par_2 ?par_0))) (and (ball ?par_2) (room ?par_1) (gripper ?par_0) (carry ?par_2 ?par_0) (at-robby ?par_1))) )
		:effect (and (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) )   (and (at ?par_2 ?par_1 ) (free ?par_0 ) (not (carry ?par_2 ?par_0 )) ) )
	)
)