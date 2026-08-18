test_that("pytekt_sum computes accurate sums", {
  expect_equal(pytekt_sum(c(1.0, 2.0, 3.0, 4.0)), 10.0)
  expect_equal(pytekt_sum(numeric(0)), 0.0)
  expect_equal(pytekt_sum(c(-5.5, 5.5, 10.0)), 10.0)
})

test_that("pytekt_dot computes correct dot product and enforces dimensions", {
  a <- c(1.0, 2.0, 3.0)
  b <- c(4.0, 5.0, 6.0)
  expect_equal(pytekt_dot(a, b), 32.0)
  expect_equal(pytekt_dot(c(1.0, 0.0), c(0.0, 1.0)), 0.0)
  expect_error(pytekt_dot(c(1.0, 2.0), c(1.0)), "equal length")
})

test_that("pytekt_norm2 computes Euclidean norm", {
  expect_equal(pytekt_norm2(c(3.0, 4.0)), 5.0)
  expect_equal(pytekt_norm2(c(0.0, 0.0, 0.0)), 0.0)
})

test_that("pytekt_mean computes arithmetic mean and handles errors", {
  expect_equal(pytekt_mean(c(2.0, 4.0, 6.0, 8.0)), 5.0)
  expect_error(pytekt_mean(numeric(0)), "vector is empty")
})

test_that("pytekt_variance calculates variance with ddof options", {
  x <- c(2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0)
  # Population variance (ddof = 0): sum((x - mean)^2) / N = 32 / 8 = 4.0
  expect_equal(pytekt_variance(x, ddof = 0), 4.0)
  # Sample variance (ddof = 1): sum((x - mean)^2) / (N - 1) = 32 / 7 = stats::var(x)
  expect_equal(pytekt_variance(x, ddof = 1), var(x), tolerance = 1e-10)
})
