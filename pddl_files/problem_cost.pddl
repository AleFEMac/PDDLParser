(define
	(problem cake-time-problem)
	
	(:domain cake-money)

	(:init (= (total-cost) 0))

	(:goal (cake))

	(:metric minimize (total-cost))
)