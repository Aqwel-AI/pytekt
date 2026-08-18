test_that("pytekt_min and pytekt_max find extrema correctly", {
  x <- c(3.0, 1.0, 4.0, 1.5, 9.0, 2.6, 5.0)
  expect_equal(pytekt_min(x), 1.0)
  expect_equal(pytekt_max(x), 9.0)
  expect_error(pytekt_min(numeric(0)), "vector is empty")
  expect_error(pytekt_max(numeric(0)), "vector is empty")
})

test_that("pytekt_argmin and pytekt_argmax return 1-based indices", {
  x <- c(10.0, 20.0, 5.0, 40.0, 50.0)
  expect_equal(pytekt_argmin(x), 3L)
  expect_equal(pytekt_argmax(x), 5L)
  
  y <- c(-100.0, 0.0, 100.0)
  expect_equal(pytekt_argmin(y), 1L)
  expect_equal(pytekt_argmax(y), 3L)
  
  expect_error(pytekt_argmin(numeric(0)), "vector is empty")
  expect_error(pytekt_argmax(numeric(0)), "vector is empty")
})
