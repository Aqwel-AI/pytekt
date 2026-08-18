#' Import Pytekt Python Module via Reticulate
#'
#' Provides direct access to the full Pytekt Python research suite
#' (machine learning models, physics, astronomy, computer vision, datasets, RAG).
#'
#' @param convert Logical. Whether to automatically convert Python objects to R objects.
#' @return A Python module object representing Pytekt.
#' @examples
#' \dontrun{
#' if (pytekt_available()) {
#'   pytekt <- import_pytekt()
#'   ds <- pytekt$datasets$load_iris()
#' }
#' }
#' @export
import_pytekt <- function(convert = TRUE) {
  if (!requireNamespace("reticulate", quietly = TRUE)) {
    stop(
      "The 'reticulate' package is required to use Pytekt's Python features.\n",
      "Please install it using: install.packages('reticulate')",
      call. = FALSE
    )
  }
  
  # Try importing 'aion' or 'pytekt' module
  mod <- tryCatch(
    reticulate::import("aion", convert = convert),
    error = function(e) {
      tryCatch(
        reticulate::import("pytekt", convert = convert),
        error = function(e2) NULL
      )
    }
  )
  
  if (is.null(mod)) {
    stop(
      "Pytekt Python module could not be found.\n",
      "Please install it using pip in your Python environment:\n",
      "  pip install aqwel-aion\n",
      "Or from R:\n",
      "  reticulate::py_install('aqwel-aion')",
      call. = FALSE
    )
  }
  
  mod
}

#' Check if Pytekt Python Module is Available
#'
#' @return Logical TRUE if Python environment has `aion` or `pytekt` installed, FALSE otherwise.
#' @examples
#' pytekt_available()
#' @export
pytekt_available <- function() {
  if (!requireNamespace("reticulate", quietly = TRUE)) {
    return(FALSE)
  }
  reticulate::py_module_available("aion") || reticulate::py_module_available("pytekt")
}

#' Get Pytekt Python Module Version
#'
#' @return Character string representing the Python package version, or NA if unavailable.
#' @examples
#' \dontrun{
#' if (pytekt_available()) {
#'   pytekt_version()
#' }
#' }
#' @export
pytekt_version <- function() {
  if (!pytekt_available()) {
    return(NA_character_)
  }
  mod <- import_pytekt(convert = TRUE)
  if (!is.null(mod$`__version__`)) {
    return(as.character(mod$`__version__`))
  }
  NA_character_
}
