test_that("aion_matrix_multiply computes matrix products correctly", {
  # A: 2x3 matrix flattened row-major:
  # [1, 2, 3]
  # [4, 5, 6]
  A <- c(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
  
  # B: 3x2 matrix flattened row-major:
  # [7,  8]
  # [9,  1]
  # [2,  3]
  B <- c(7.0, 8.0, 9.0, 1.0, 2.0, 3.0)
  
  # Result (2x2):
  # [1*7+2*9+3*2, 1*8+2*1+3*3] = [31, 19]
  # [4*7+5*9+6*2, 4*8+5*1+6*3] = [85, 55]
  res <- aion_matrix_multiply(A, B, 2, 3, 2)
  expect_equal(res, c(31.0, 19.0, 85.0, 55.0))
})

test_that("aion_matrix_multiply raises error on mismatched dimensions", {
  A <- c(1.0, 2.0, 3.0, 4.0)
  B <- c(1.0, 2.0)
  expect_error(aion_matrix_multiply(A, B, 2, 2, 2), "dimension mismatch")
})
