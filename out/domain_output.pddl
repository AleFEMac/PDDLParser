(define (domain cake-money)

	(:predicates (ingredients) (no-cake) (cake) (baked-cake) (frosted-cake))

	(:action buy-cake
		:precondition (not (cake))
		:effect (and    (cake)    (increase (total-cost) 25)   )
	)
	
	(:action bake-cake
		:precondition (and (cake) (not (baked-cake)))
		:effect (and (baked-cake) (increase (total-cost) 10))
	)
	
	(:action frost-cake
		:precondition (and (baked-cake) (not (frosted-cake)))
		:effect (and (frosted-cake) (increase (total-cost) 12))
	)
	
	(:action buy-cake_bake-cake
		:precondition (and (not (cake)) (not (baked-cake)))
		:effect (and (cake) (baked-cake) (increase (total-cost) 35))
	)
	
	(:action buy-cake_frost-cake
		:precondition (and (not (cake)) (baked-cake) (not (frosted-cake)))
		:effect (and (cake) (frosted-cake) (increase (total-cost) 37))
	)
	
	(:action bake-cake_frost-cake
		:precondition (and (cake) (not (baked-cake)) (not (frosted-cake)))
		:effect (and (baked-cake) (frosted-cake) (increase (total-cost) 22))
	)
	
	(:action frost-cake_buy-cake
		:precondition (and (baked-cake) (not (frosted-cake)) (not (cake)))
		:effect (and (frosted-cake) (cake) (increase (total-cost) 37))
	)
)