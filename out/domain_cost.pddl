(define (domain cake-money)

	(:predicates (ingredients) (no-cake) (cake) (baked-cake) (frosted-cake))

	(:action buy-cake
		:precondition (not (cake))
		:effect (and   (cake) (increase (total-cost) 25)   )
	)
	
	(:action buy-cake-useless
		:precondition (cake)
		:effect (and   (not (cake)) (increase (total-cost) 10)   )
	)
	
	(:action bake-cake
		:precondition (and (cake) (not (baked-cake)))
		:effect (and (baked-cake) (increase (total-cost) 10))
	)
	
	(:action frost-cake
		:precondition (and (baked-cake) (not (frosted-cake)))
		:effect (and (frosted-cake) (increase (total-cost) 12))
	)
)