/-!
# QEC distance claim scaffold (toy CSS instance).
-/

namespace QSpecBench

/-- Declared minimum distance parameter for the small CSS toy certificate. -/
def cssDeclaredDistance : Nat := 3

theorem css_declared_distance_at_least_three : cssDeclaredDistance ≥ 3 := by decide

end QSpecBench
