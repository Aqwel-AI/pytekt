pkgname <- "pytekt"
source(file.path(R.home("share"), "R", "examples-header.R"))
options(warn = 1)
library('pytekt')

base::assign(".oldSearch", base::search(), pos = 'CheckExEnv')
base::assign(".old_wd", base::getwd(), pos = 'CheckExEnv')
cleanEx()
nameEx("import_pytekt")
### * import_pytekt

flush(stderr()); flush(stdout())

### Name: import_pytekt
### Title: Import Pytekt Python Module via Reticulate
### Aliases: import_pytekt

### ** Examples

## Not run: 
##D if (pytekt_available()) {
##D   pytekt <- import_pytekt()
##D   ds <- pytekt$datasets$load_iris()
##D }
## End(Not run)



cleanEx()
nameEx("pytekt_argmax")
### * pytekt_argmax

flush(stderr()); flush(stdout())

### Name: pytekt_argmax
### Title: Fast Argmax (1-indexed)
### Aliases: pytekt_argmax

### ** Examples

pytekt_argmax(c(4.0, 1.0, 8.0, 2.0))



cleanEx()
nameEx("pytekt_argmin")
### * pytekt_argmin

flush(stderr()); flush(stdout())

### Name: pytekt_argmin
### Title: Fast Argmin (1-indexed)
### Aliases: pytekt_argmin

### ** Examples

pytekt_argmin(c(4.0, 1.0, 8.0, 2.0))



cleanEx()
nameEx("pytekt_available")
### * pytekt_available

flush(stderr()); flush(stdout())

### Name: pytekt_available
### Title: Check if Pytekt Python Module is Available
### Aliases: pytekt_available

### ** Examples

pytekt_available()



cleanEx()
nameEx("pytekt_chunk_statistics")
### * pytekt_chunk_statistics

flush(stderr()); flush(stdout())

### Name: pytekt_chunk_statistics
### Title: Fast Chunk Statistics
### Aliases: pytekt_chunk_statistics

### ** Examples

pytekt_chunk_statistics(c(1.0, 2.0, 3.0, 4.0, 5.0, 6.0), chunk_size = 2)



cleanEx()
nameEx("pytekt_cosine_similarity")
### * pytekt_cosine_similarity

flush(stderr()); flush(stdout())

### Name: pytekt_cosine_similarity
### Title: Fast Cosine Similarity
### Aliases: pytekt_cosine_similarity

### ** Examples

pytekt_cosine_similarity(c(1.0, 0.0), c(1.0, 1.0))



cleanEx()
nameEx("pytekt_dot")
### * pytekt_dot

flush(stderr()); flush(stdout())

### Name: pytekt_dot
### Title: Fast Dot Product of Two Vectors
### Aliases: pytekt_dot

### ** Examples

pytekt_dot(c(1.0, 2.0), c(3.0, 4.0))



cleanEx()
nameEx("pytekt_euclidean_distance")
### * pytekt_euclidean_distance

flush(stderr()); flush(stdout())

### Name: pytekt_euclidean_distance
### Title: Fast Euclidean Distance
### Aliases: pytekt_euclidean_distance

### ** Examples

pytekt_euclidean_distance(c(0.0, 0.0), c(3.0, 4.0))



cleanEx()
nameEx("pytekt_histogram")
### * pytekt_histogram

flush(stderr()); flush(stdout())

### Name: pytekt_histogram
### Title: Fast Streaming Histogram
### Aliases: pytekt_histogram

### ** Examples

pytekt_histogram(c(1.0, 2.0, 3.0, 4.0, 5.0), bins = 5, lo = 1.0, hi = 5.0)



cleanEx()
nameEx("pytekt_matrix_multiply")
### * pytekt_matrix_multiply

flush(stderr()); flush(stdout())

### Name: pytekt_matrix_multiply
### Title: Fast Matrix Multiplication (Row-Major flattened matrices)
### Aliases: pytekt_matrix_multiply

### ** Examples

pytekt_matrix_multiply(c(1, 2, 3, 4), c(5, 6, 7, 8), 2, 2, 2)



cleanEx()
nameEx("pytekt_max")
### * pytekt_max

flush(stderr()); flush(stdout())

### Name: pytekt_max
### Title: Fast Maximum
### Aliases: pytekt_max

### ** Examples

pytekt_max(c(4.0, 1.0, 8.0, 2.0))



cleanEx()
nameEx("pytekt_mean")
### * pytekt_mean

flush(stderr()); flush(stdout())

### Name: pytekt_mean
### Title: Fast Mean
### Aliases: pytekt_mean

### ** Examples

pytekt_mean(c(1.0, 2.0, 3.0, 4.0))



cleanEx()
nameEx("pytekt_min")
### * pytekt_min

flush(stderr()); flush(stdout())

### Name: pytekt_min
### Title: Fast Minimum
### Aliases: pytekt_min

### ** Examples

pytekt_min(c(4.0, 1.0, 8.0, 2.0))



cleanEx()
nameEx("pytekt_norm2")
### * pytekt_norm2

flush(stderr()); flush(stdout())

### Name: pytekt_norm2
### Title: Fast L2 Norm
### Aliases: pytekt_norm2

### ** Examples

pytekt_norm2(c(3.0, 4.0))



cleanEx()
nameEx("pytekt_prefix_sum")
### * pytekt_prefix_sum

flush(stderr()); flush(stdout())

### Name: pytekt_prefix_sum
### Title: Fast Cumulative Prefix Sum
### Aliases: pytekt_prefix_sum

### ** Examples

pytekt_prefix_sum(c(1.0, 2.0, 3.0, 4.0))



cleanEx()
nameEx("pytekt_rolling_mean")
### * pytekt_rolling_mean

flush(stderr()); flush(stdout())

### Name: pytekt_rolling_mean
### Title: Fast Rolling Mean
### Aliases: pytekt_rolling_mean

### ** Examples

pytekt_rolling_mean(c(1.0, 2.0, 3.0, 4.0, 5.0), window = 3)



cleanEx()
nameEx("pytekt_rolling_sum")
### * pytekt_rolling_sum

flush(stderr()); flush(stdout())

### Name: pytekt_rolling_sum
### Title: Fast Rolling Sum
### Aliases: pytekt_rolling_sum

### ** Examples

pytekt_rolling_sum(c(1.0, 2.0, 3.0, 4.0, 5.0), window = 3)



cleanEx()
nameEx("pytekt_std")
### * pytekt_std

flush(stderr()); flush(stdout())

### Name: pytekt_std
### Title: Fast Standard Deviation
### Aliases: pytekt_std

### ** Examples

pytekt_std(c(1.0, 2.0, 3.0, 4.0), ddof = 1)



cleanEx()
nameEx("pytekt_sum")
### * pytekt_sum

flush(stderr()); flush(stdout())

### Name: pytekt_sum
### Title: Fast Sum of Numeric Vector
### Aliases: pytekt_sum

### ** Examples

pytekt_sum(c(1.0, 2.0, 3.0, 4.0))



cleanEx()
nameEx("pytekt_variance")
### * pytekt_variance

flush(stderr()); flush(stdout())

### Name: pytekt_variance
### Title: Fast Variance
### Aliases: pytekt_variance

### ** Examples

pytekt_variance(c(1.0, 2.0, 3.0, 4.0), ddof = 1)



cleanEx()
nameEx("pytekt_version")
### * pytekt_version

flush(stderr()); flush(stdout())

### Name: pytekt_version
### Title: Get Pytekt Python Module Version
### Aliases: pytekt_version

### ** Examples

## Not run: 
##D if (pytekt_available()) {
##D   pytekt_version()
##D }
## End(Not run)



### * <FOOTER>
###
cleanEx()
options(digits = 7L)
base::cat("Time elapsed: ", proc.time() - base::get("ptime", pos = 'CheckExEnv'),"\n")
grDevices::dev.off()
###
### Local variables: ***
### mode: outline-minor ***
### outline-regexp: "\\(> \\)?### [*]+" ***
### End: ***
quit('no')
