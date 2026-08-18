test_that("pytekt_std computes standard deviation correctly", {
  x <- c(2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0)
  expect_equal(pytekt_std(x, ddof = 0), 2.0)
  expect_equal(pytekt_std(x, ddof = 1), stats::sd(x), tolerance = 1e-10)
  expect_error(pytekt_std(c(1.0), ddof = 1), "length must be > ddof")
})

test_that("pytekt_chunk_statistics calculates block summaries accurately", {
  x <- c(1.0, 3.0, 5.0, 7.0, 9.0)
  res <- pytekt_chunk_statistics(x, chunk_size = 2)
  
  # Chunks: [1, 3], [5, 7], [9]
  expect_equal(res$mean, c(2.0, 6.0, 9.0))
  expect_equal(res$min, c(1.0, 5.0, 9.0))
  expect_equal(res$max, c(3.0, 7.0, 9.0))
  expect_equal(res$chunk_size, 2L)
  
  expect_error(pytekt_chunk_statistics(x, chunk_size = 0), "chunk_size must be > 0")
})
