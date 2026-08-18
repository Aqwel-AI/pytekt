test_that("pytekt_available and version behave safely", {
  avail <- pytekt_available()
  expect_true(is.logical(avail))
  
  ver <- pytekt_version()
  expect_true(is.character(ver))
})
