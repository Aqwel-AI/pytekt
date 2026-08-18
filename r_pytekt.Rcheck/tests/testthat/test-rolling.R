test_that("pytekt_prefix_sum computes cumulative prefix sums", {
  x <- c(1.0, 2.0, 3.0, 4.0, 5.0)
  expect_equal(pytekt_prefix_sum(x), c(1.0, 3.0, 6.0, 10.0, 15.0))
  expect_equal(pytekt_prefix_sum(numeric(0)), numeric(0))
})

test_that("pytekt_rolling_sum calculates rolling window sums", {
  x <- c(1.0, 2.0, 3.0, 4.0, 5.0)
  # Window = 3 -> valid outputs length is length(x) - window + 1 = 3
  # sums: 1+2+3=6, 2+3+4=9, 3+4+5=12
  expect_equal(pytekt_rolling_sum(x, 3), c(6.0, 9.0, 12.0))
})

test_that("pytekt_rolling_mean calculates rolling window averages", {
  x <- c(2.0, 4.0, 6.0, 8.0, 10.0)
  # Window = 2 -> 3, 5, 7, 9
  expect_equal(pytekt_rolling_mean(x, 2), c(3.0, 5.0, 7.0, 9.0))
})
