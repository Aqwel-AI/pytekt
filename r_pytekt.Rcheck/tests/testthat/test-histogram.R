test_that("pytekt_histogram computes bin distributions accurately", {
  # Range [0, 10] with 5 bins: [0,2), [2,4), [4,6), [6,8), [8,10]
  x <- c(1.0, 1.5, 3.0, 5.0, 5.5, 7.0, 9.0, 10.0, 15.0) # 15.0 is out of bounds
  counts <- pytekt_histogram(x, bins = 5, lo = 0.0, hi = 10.0)
  # Bin 0: 1.0, 1.5 -> 2
  # Bin 1: 3.0 -> 1
  # Bin 2: 5.0, 5.5 -> 2
  # Bin 3: 7.0 -> 1
  # Bin 4: 9.0, 10.0 -> 2
  expect_equal(as.integer(counts), c(2L, 1L, 2L, 1L, 2L))
})
