(define (domain cake-money)

	(:predicates (type_food ?c) (ingredients ?c) (no-cake ?c) (cake ?c) (baked-cake ?c) (frosted-cake ?c))

	(:action buy-cake
		:parameters ( ?c )
		:precondition (and (type_food ?c) (not (cake ?c)) (ingredients ?c))
		:effect (and (cake ?c) (not (ingredients ?c)) (increase (total-cost) 25))
	)
	
	(:action bake-cake
		:parameters ( ?c )
		:precondition (and (type_food ?c) (cake ?c) (not (baked-cake ?c)))
		:effect (and (baked-cake ?c) (not (cake ?c)) (increase (total-cost) 10))
	)
	
	(:action frost-cake
		:parameters ( ?c )
		:precondition (and (type_food ?c) (baked-cake ?c) (not (frosted-cake ?c)))
		:effect (and (frosted-cake ?c) (not (baked-cake ?c)) (increase (total-cost) 12))
	)
	
	(:action buy-cake_bake-cake
		:parameters ( ?par_0 )
		:precondition (and (type_food ?par_0) (not (cake ?par_0)) (ingredients ?par_0) (not (baked-cake ?par_0)))
		:effect (and (not (cake ?par_0)) (not (ingredients ?par_0)) (baked-cake ?par_0) (increase (total-cost) 35))
	)
	
	(:action buy-cake_frost-cake
		:parameters ( ?par_0 )
		:precondition (and (type_food ?par_0) (not (cake ?par_0)) (ingredients ?par_0) (baked-cake ?par_0) (not (frosted-cake ?par_0)))
		:effect (and (cake ?par_0) (not (ingredients ?par_0)) (frosted-cake ?par_0) (not (baked-cake ?par_0)) (increase (total-cost) 37))
	)
	
	(:action bake-cake_frost-cake
		:parameters ( ?par_0 )
		:precondition (and (type_food ?par_0) (cake ?par_0) (not (baked-cake ?par_0)) (not (frosted-cake ?par_0)))
		:effect (and (not (baked-cake ?par_0)) (not (cake ?par_0)) (frosted-cake ?par_0) (increase (total-cost) 22))
	)
	
	(:action frost-cake_buy-cake
		:parameters ( ?par_0 )
		:precondition (and (type_food ?par_0) (baked-cake ?par_0) (not (frosted-cake ?par_0)) (not (cake ?par_0)) (ingredients ?par_0))
		:effect (and (frosted-cake ?par_0) (not (baked-cake ?par_0)) (cake ?par_0) (not (ingredients ?par_0)) (increase (total-cost) 37))
	)
)