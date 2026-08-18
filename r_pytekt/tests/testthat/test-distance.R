test_that("pytekt_euclidean_distance computes Euclidean distance accurately", {
  a <- c(0.0, 0.0)
  b <- c(3.0, 4.0)
  expect_equal(pytekt_euclidean_distance(a, b), 5.0)
  
  c <- c(1.0, 2.0, 3.0)
  expect_equal(pytekt_euclidean_distance(c, c), 0.0)
  
  expect_error(pytekt_euclidean_distance(a, c), "equal length")
})

test_that("pytekt_cosine_similarity computes angular similarity accurately", {
  a <- c(1.0, 0.0)
  b <- c(0.0, 1.0)
  expect_equal(pytekt_cosine_similarity(a, b), 0.0) # orthogonal
  
  c <- c(2.0, 2.0)
  d <- c(5.0, 5.0)
  expect_equal(pytekt_cosine_similarity(c, d), 1.0) # parallel
  
  e <- c(1.0, 0.0)
  f <- c(-1.0, 0.0)
  expect_equal(pytekt_cosine_similarity(e, f), -1.0) # opposite
  
  expect_equal(pytekt_cosine_similarity(c(0.0, 0.0), c(1.0, 1.0)), 0.0) # zero vector
  expect_error(pytekt_cosine_similarity(a, c(1.0, 2.0, 3.0)), "equal length")
})
